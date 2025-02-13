"""Module for analyzing conversations between characters."""

from dataclasses import dataclass
from typing import List, Dict, Set, Tuple
from .character import Character

@dataclass
class Conversation:
    """Represents a conversation between characters."""
    
    participants: Set[Character]
    dialogue: List[str]
    about_men: bool = False

class ConversationAnalyzer:
    """Analyzes conversations between characters."""

    def __init__(self):
        """Initialize the conversation analyzer."""
        # Male-related words to check for conversations about men
        self.male_topic_indicators = {
            "he", "him", "his", "himself", "boy", "man", "guy", "father",
            "brother", "uncle", "son", "husband", "boyfriend", "mr", "sir",
            "dad", "daddy", "grandpa", "grandfather"
        }

    def extract_conversations(
        self, 
        character_lines: Dict[str, List[str]], 
        characters: Dict[str, Character]
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
                    conversations.append(
                        Conversation(
                            participants=current_participants.copy(),
                            dialogue=current_dialogue.copy(),
                            about_men=self._is_about_men(current_dialogue)
                        )
                    )
            
            # Reset if speaker changes or there's a large gap
            if not last_speaker or name != last_speaker:
                if len(current_dialogue) > 1:  # Keep at least one previous line for context
                    current_dialogue = [current_dialogue[-1], line]
                    current_participants = {characters[last_speaker], current_char} if last_speaker else {current_char}
            
            last_speaker = name

            # If we're at the end, check if we should add the final conversation
            if i == len(sequence) - 1 and len(current_participants) >= 2:
                conversations.append(
                    Conversation(
                        participants=current_participants.copy(),
                        dialogue=current_dialogue.copy(),
                        about_men=self._is_about_men(current_dialogue)
                    )
                )

        return conversations

    def _is_about_men(self, dialogue: List[str]) -> bool:
        """Determine if conversation is primarily about men.
        
        Args:
            dialogue: List of dialogue lines.
            
        Returns:
            True if conversation appears to be about men.
        """
        male_ref_count = 0
        total_words = 0
        
        for line in dialogue:
            words = line.lower().split()
            total_words += len(words)
            
            # Count words that indicate talking about men
            male_ref_count += sum(1 for word in words if word in self.male_topic_indicators)
        
        # Consider it about men if male references exceed threshold
        if total_words > 0:
            male_ref_ratio = male_ref_count / total_words
            return male_ref_ratio > 0.1  # Threshold for "about men"
        
        return False
