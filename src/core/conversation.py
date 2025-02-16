"""Module for analyzing conversations between characters."""

from dataclasses import dataclass
from typing import List, Dict, Set
from .character import Character
from .llm_helper import is_conversation_about_men
from .exceptions import ConversationError
from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class Conversation:
    """Represents a conversation between characters."""

    participants: Set[Character]
    dialogue: List[str]
    about_men: bool = False
    context: str = ""  # Optional context about the conversation

    def __str__(self) -> str:
        """Return a string representation of the conversation."""
        participant_names = ", ".join(char.name for char in self.participants)
        return f"Conversation between {participant_names} ({'about men' if self.about_men else 'not about men'})"


class ConversationAnalyzer:
    """Analyzes conversations between characters."""

    def __init__(self):
        """Initialize the conversation analyzer."""
        # Male-related words for rule-based topic detection
        self.male_topic_indicators = {
            "he",
            "him",
            "his",
            "himself",
            "boy",
            "man",
            "guy",
            "father",
            "brother",
            "uncle",
            "son",
            "husband",
            "boyfriend",
            "mr",
            "sir",
            "dad",
            "daddy",
            "grandpa",
            "grandfather",
        }
        logger.debug("Initialized ConversationAnalyzer with male topic indicators")

    def extract_conversations(
        self, character_lines: Dict[str, List[str]], characters: Dict[str, Character]
    ) -> List[Conversation]:
        """Extract conversations from character lines.

        Args:
            character_lines: Dictionary mapping character names to their lines.
            characters: Dictionary mapping character names to Character objects.

        Returns:
            List of Conversation objects.
        """
        # Convert to sequential dialogue
        sequence = []
        for name, lines in character_lines.items():
            for line in lines:
                if name in characters:
                    sequence.append((name, line))

        conversations = []
        if len(sequence) < 2:
            return conversations

        try:
            # Find continuous conversations
            current_participants = set()
            current_dialogue = []
            last_speaker = None

            for i, (name, line) in enumerate(sequence):
                current_char = characters[name]

                # Always add current character and line
                current_participants.add(current_char)
                current_dialogue.append(line)

                # Check if this is part of the current conversation
                if last_speaker and name != last_speaker:
                    # We have a back-and-forth between characters
                    if len(current_participants) >= 2:
                        logger.debug(
                            f"Found conversation between {len(current_participants)} characters"
                        )
                        context = f"Conversation at sequence {i}"
                        about_men = self._analyze_topic(current_dialogue, context)

                        conversations.append(
                            Conversation(
                                participants=current_participants.copy(),
                                dialogue=current_dialogue.copy(),
                                about_men=about_men,
                                context=context,
                            )
                        )

                # Reset if speaker changes or there's a large gap
                if not last_speaker or name != last_speaker:
                    if (
                        len(current_dialogue) > 1
                    ):  # Keep at least one previous line for context
                        current_dialogue = [current_dialogue[-1], line]
                        current_participants = (
                            {characters[last_speaker], current_char}
                            if last_speaker
                            else {current_char}
                        )

                last_speaker = name

                # If we're at the end, check if we should add the final conversation
                if i == len(sequence) - 1 and len(current_participants) >= 2:
                    context = "Final conversation in sequence"
                    about_men = self._analyze_topic(current_dialogue, context)

                    conversations.append(
                        Conversation(
                            participants=current_participants.copy(),
                            dialogue=current_dialogue.copy(),
                            about_men=about_men,
                            context=context,
                        )
                    )
        except Exception as e:
            logger.error(f"Error extracting conversations: {e}")
            raise ConversationError(f"Failed to extract conversations: {e}") from e

        return conversations

    def _analyze_topic(self, dialogue: List[str], context: str) -> bool:
        """Analyze conversation topic using LLM with fallback to rule-based.

        Args:
            dialogue: List of dialogue lines to analyze.
            context: Context information about the conversation.

        Returns:
            True if the conversation is determined to be about men.
        """
        try:
            about_men = is_conversation_about_men(dialogue)
            logger.debug(f"LLM topic analysis result for {context}: {about_men}")
            return about_men
        except Exception as e:
            logger.warning(
                f"LLM topic analysis failed for {context}, falling back to rule-based: {e}"
            )
            return self._rule_based_topic_analysis(dialogue)

    def _rule_based_topic_analysis(self, dialogue: List[str]) -> bool:
        """Rule-based analysis of conversation topics.

        Args:
            dialogue: List of dialogue lines to analyze.

        Returns:
            True if the conversation appears to be about men based on keyword analysis.
        """
        male_ref_count = 0
        total_words = 0

        for line in dialogue:
            words = line.lower().split()
            total_words += len(words)
            male_ref_count += sum(
                1 for word in words if word in self.male_topic_indicators
            )

        if total_words > 0:
            male_ref_ratio = male_ref_count / total_words
            result = male_ref_ratio > 0.1  # Threshold for "about men"
            logger.debug(
                f"Rule-based analysis: {male_ref_count}/{total_words} male references = {male_ref_ratio:.2%}"
            )
            return result

        return False
