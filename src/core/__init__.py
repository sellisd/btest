"""Core functionality for the Bechdel test analyzer."""

from .text_processor import TextProcessor
from .character import Character, CharacterClassifier
from .conversation import ConversationAnalyzer
from .analyzer import BechdelAnalyzer

__all__ = [
    "TextProcessor",
    "Character",
    "CharacterClassifier",
    "ConversationAnalyzer",
    "BechdelAnalyzer",
]
