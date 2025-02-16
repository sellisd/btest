"""Module for analyzing scripts using the Bechdel test criteria."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .text_processor import TextProcessor
from .character import Character, CharacterClassifier
from .conversation import Conversation, ConversationAnalyzer
from .llm_helper import validate_bechdel_result
from .script_finder import ScriptFinder


@dataclass
class BechdelResult:
    """Results of Bechdel test analysis."""

    passes_test: bool
    female_characters: List[Character]
    conversations: Optional[List[Conversation]] = None
    failure_reasons: Optional[List[str]] = None


class BechdelAnalyzer:
    """Analyzes movie scripts using Bechdel test criteria."""

    def __init__(self):
        """Initialize analyzer components."""
        self.text_processor = TextProcessor()
        self.character_classifier = CharacterClassifier()
        self.conversation_analyzer = ConversationAnalyzer()

    def analyze_script(self, script_text: str) -> BechdelResult:
        """Analyze script text using Bechdel test criteria.

        Args:
            script_text: Raw script text to analyze.

        Returns:
            BechdelResult containing analysis results.
        """
        # Extract and classify characters
        character_lines = self.text_processor.process_script(script_text)
        characters = {}
        female_characters = []

        # Create and classify characters with their lines
        for name, lines in character_lines.items():
            char = Character(name=name, lines=lines)
            char = self.character_classifier.classify_character(char, script_text)
            characters[name] = char
            if char.gender == "female":
                female_characters.append(char)

        # Extract all conversations
        conversations = self.conversation_analyzer.extract_conversations(
            character_lines, characters
        )

        # Begin Bechdel test checks
        failure_reasons = []

        # Criterion 1: At least two named female characters
        if len(female_characters) < 2:
            failure_reasons.append("Fewer than two female characters found")
            return BechdelResult(
                passes_test=False,
                female_characters=female_characters,
                conversations=conversations,
                failure_reasons=failure_reasons,
            )

        # Criterion 2: These women talk to each other
        female_conversations = [
            conv
            for conv in conversations
            if all(char.gender == "female" for char in conv.participants)
            and len(conv.participants) >= 2
        ]

        if not female_conversations:
            failure_reasons.append("No conversations between female characters found")
            return BechdelResult(
                passes_test=False,
                female_characters=female_characters,
                conversations=conversations,
                failure_reasons=failure_reasons,
            )

        # Criterion 3: Their conversation isn't about men
        non_male_conversations = [
            conv for conv in female_conversations if not conv.about_men
        ]

        if not non_male_conversations:
            failure_reasons.append(
                "All conversations between female characters are about men"
            )
            return BechdelResult(
                passes_test=False,
                female_characters=female_characters,
                conversations=conversations,
                failure_reasons=failure_reasons,
            )

        # Base result from rule-based analysis
        result = BechdelResult(
            passes_test=True,
            female_characters=female_characters,
            conversations=conversations,
        )

        # Validate result using LLM
        try:
            # Extract conversation texts for validation
            conv_texts = [conv.dialogue for conv in non_male_conversations]
            female_char_names = [char.name for char in female_characters]

            # Get LLM validation of the result
            validated = validate_bechdel_result(
                female_char_names,
                conv_texts,
                True,  # Original pass result
            )

            if not validated:
                result.passes_test = False
                result.failure_reasons = ["LLM validation determined test should fail"]
        except Exception:
            # If LLM validation fails, stick with rule-based result
            pass

        return result

    def analyze_script_file(self, file_path: str) -> BechdelResult:
        """Analyze script from file.

        Args:
            file_path: Path to script file.

        Returns:
            BechdelResult containing analysis results.
        """
        script_text = Path(file_path).read_text()
        return self.analyze_script(script_text)

    def analyze_movie(self, title: str) -> Optional[BechdelResult]:
        """Analyze movie by title using the script finder.

        Args:
            title: Movie title to search and analyze.

        Returns:
            BechdelResult if script is found, None otherwise.
        """
        finder = ScriptFinder()
        script = finder.find_script(title)

        if script is None:
            return None

        return self.analyze_script(script)
