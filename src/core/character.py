"""Module for character analysis and gender detection."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from .llm_helper import detect_gender

class Character(BaseModel):
    """Represents a character in the script."""
    
    name: str
    lines: Optional[List[str]] = Field(default=None)
    gender: str = Field(default="unknown")
    
    def __hash__(self):
        """Hash based on character name."""
        return hash(self.name)
    
    model_config = {
        "arbitrary_types_allowed": True
    }

class CharacterClassifier:
    """Analyzes and classifies characters based on name and dialogue context."""

    def __init__(self, names_dataset_path: Optional[str] = None):
        """Initialize the character classifier.
        
        Args:
            names_dataset_path: Optional path to names-gender dataset.
        """
        # Common female and male names for basic gender detection
        self.female_names = {
            "mary", "patricia", "linda", "barbara", "elizabeth", "jennifer", "maria",
            "susan", "margaret", "dorothy", "sarah", "jessica", "helen", "nancy",
            "betty", "karen", "lisa", "anna", "emma", "emily", "alice", "jane",
            "anne", "jean", "judy", "rose", "catherine", "martha"
        }
        
        self.male_names = {
            "james", "john", "robert", "michael", "william", "david", "richard",
            "charles", "joseph", "thomas", "george", "donald", "kenneth", "steven",
            "edward", "brian", "ronald", "anthony", "kevin", "jason", "matthew",
            "gary", "timothy", "jose", "larry", "jeffrey", "frank", "scott", "eric"
        }
        
        # Gender-indicating words
        self.female_indicators = {
            "she", "her", "hers", "herself", "girl", "woman", "lady", "mother",
            "sister", "aunt", "daughter", "wife", "girlfriend", "mrs", "miss", "ms"
        }
        
        self.male_indicators = {
            "he", "him", "his", "himself", "boy", "man", "guy", "father",
            "brother", "uncle", "son", "husband", "boyfriend", "mr", "sir"
        }

    def classify_character(self, character: Character, script_text: Optional[str] = None) -> Character:
        """Determine character's likely gender based on name and context.
        
        Args:
            character: Character object to classify.
            script_text: Optional full script text for context.
            
        Returns:
            Character object with gender field set.
        """
        # Try to determine gender from name
        name_gender = self._get_name_gender(character.name)
        if name_gender != "unknown":
            character.gender = name_gender
            return character
        
        # If we have dialogue lines, analyze them for gender indicators
        if character.lines:
            dialogue_gender = self._analyze_dialogue_for_gender(character.lines)
            if dialogue_gender != "unknown":
                character.gender = dialogue_gender
                return character
        
        # If we have script context, try to find gender indicators there
        if script_text:
            context_gender = self._analyze_context_for_gender(character.name, script_text)
            if context_gender != "unknown":
                character.gender = context_gender
                return character

        # Use LLM as a final fallback for gender detection
        if script_text:
            # Create context from character's lines and surrounding text
            context = "\n".join(character.lines) if character.lines else script_text
            llm_gender = detect_gender(character.name, context)
            if llm_gender != "unknown":
                character.gender = llm_gender
                return character
        
        # Keep as unknown if no confident determination
        return character

    def _get_name_gender(self, name: str) -> str:
        """Determine gender based on character name.
        
        Args:
            name: Character name to analyze.
            
        Returns:
            Gender string ("male", "female", or "unknown").
        """
        # Clean and normalize the name
        first_name = name.lower().split()[0]
        
        if first_name in self.female_names:
            return "female"
        elif first_name in self.male_names:
            return "male"
        
        # Check common name endings
        if first_name.endswith(("a", "ie", "y", "i")) and not first_name.endswith(("by", "ey", "dy", "ty")):
            return "female"
        elif first_name.endswith(("son", "ton", "er", "or", "en")):
            return "male"
        
        return "unknown"

    def _analyze_dialogue_for_gender(self, lines: List[str]) -> str:
        """Analyze character's dialogue for gender indicators.
        
        Args:
            lines: List of dialogue lines.
            
        Returns:
            Gender string ("male", "female", or "unknown").
        """
        female_count = 0
        male_count = 0
        
        for line in lines:
            words = line.lower().split()
            
            # Count gender indicators
            female_count += sum(1 for word in words if word in self.female_indicators)
            male_count += sum(1 for word in words if word in self.male_indicators)
        
        # Determine gender based on indicator ratios
        if female_count > male_count * 2:
            return "female"
        elif male_count > female_count * 2:
            return "male"
        
        return "unknown"

    def _analyze_context_for_gender(self, name: str, text: str) -> str:
        """Analyze script context for gender indicators around character mentions.
        
        Args:
            name: Character name to look for.
            text: Full script text.
            
        Returns:
            Gender string ("male", "female", or "unknown").
        """
        # Look for gender indicators in the same sentence as character mentions
        sentences = text.split('.')
        female_count = 0
        male_count = 0
        
        for sentence in sentences:
            if name in sentence:
                words = sentence.lower().split()
                female_count += sum(1 for word in words if word in self.female_indicators)
                male_count += sum(1 for word in words if word in self.male_indicators)
        
        # Determine gender based on context indicators
        if female_count > male_count * 2:
            return "female"
        elif male_count > female_count * 2:
            return "male"
        
        return "unknown"
