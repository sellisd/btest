"""Module for processing and extracting dialogue from movie scripts."""

import re
from typing import Dict, List, Tuple

class TextProcessor:
    """Handles text processing and dialogue extraction from movie scripts."""

    def __init__(self):
        """Initialize the text processor with regex patterns."""
        self.dialogue_pattern = re.compile(
            r"(?P<character>[A-Z][A-Z\s]+):\s*(?P<dialogue>.*?)(?=\n[A-Z][A-Z\s]+:|$)",
            re.MULTILINE | re.DOTALL
        )
        
        self.male_indicators = {
            "he", "him", "his", "himself", "boy", "man", "guy", "father",
            "brother", "uncle", "son", "husband", "boyfriend", "mr", "sir"
        }

    def extract_dialogues(self, text: str) -> List[Tuple[str, str]]:
        """Extract character-dialogue pairs from text.
        
        Args:
            text: Raw script text.
            
        Returns:
            List of tuples containing (character, dialogue).
        """
        matches = self.dialogue_pattern.finditer(text)
        dialogues = []
        
        for match in matches:
            character = match.group("character").strip()
            dialogue = match.group("dialogue").strip()
            dialogue = self._clean_text(dialogue)
            if dialogue:  # Only add non-empty dialogues
                dialogues.append((character, dialogue))
        
        return dialogues

    def _clean_text(self, text: str) -> str:
        """Clean and normalize dialogue text.
        
        Args:
            text: Raw dialogue text.
            
        Returns:
            Cleaned and normalized text.
        """
        # Remove parenthetical directions
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Remove multiple whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text

    def process_script(self, text: str) -> Dict[str, List[str]]:
        """Process full script and organize dialogues by character.
        
        Args:
            text: Complete script text.
            
        Returns:
            Dictionary mapping characters to their lines of dialogue.
        """
        dialogues = self.extract_dialogues(text)
        character_lines: Dict[str, List[str]] = {}
        
        for character, line in dialogues:
            if character not in character_lines:
                character_lines[character] = []
            character_lines[character].append(line)
        
        return character_lines

    def contains_male_references(self, text: str) -> bool:
        """Check if text contains references to male characters.
        
        Args:
            text: Text to analyze.
            
        Returns:
            True if text contains male references, False otherwise.
        """
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        words = text_lower.split()
        
        # Check for male indicators
        return any(word in self.male_indicators for word in words)

    def get_named_entities(self, text: str) -> List[str]:
        """Extract potential person names from text using simple heuristics.
        
        Args:
            text: Text to analyze.
            
        Returns:
            List of potential person names.
        """
        # Look for capitalized words that might be names
        # This is a simple heuristic and won't be as accurate as spaCy
        words = text.split()
        potential_names = []
        
        for word in words:
            # Look for capitalized words not at the start of sentences
            if (word.istitle() and 
                len(word) > 1 and 
                not word.isupper() and 
                not word.endswith(('.', '!', '?'))):
                potential_names.append(word)
        
