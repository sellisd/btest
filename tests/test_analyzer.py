"""Test module for the Bechdel test analyzer."""

from pathlib import Path
import pytest

from src.core.text_processor import TextProcessor
from src.core.character import Character, CharacterClassifier
from src.core.conversation import ConversationAnalyzer
from src.core.analyzer import BechdelAnalyzer, BechdelResult

# Path to sample script file
SCRIPT_PATH = Path("data/sample_scripts/sample_script.txt")

@pytest.fixture
def sample_script():
    """Sample script text for testing."""
    return """NARRATOR: The small coffee shop buzzes with morning activity.

SARAH: Hey Mary! I've been working on this new quantum theory in the lab. I have some ideas to share.

MARY: That sounds fascinating! Let's discuss your research. What have you discovered?

SARAH: Perfect! I'd love to hear your thoughts on the experimental setup.

MARY: Well, I've been working with similar theories. Let's compare notes."""

@pytest.fixture
def analyzer():
    """Create a BechdelAnalyzer instance for testing."""
    return BechdelAnalyzer()

def test_text_processor_extracts_dialogues(sample_script):
    """Test that TextProcessor correctly extracts character dialogues."""
    processor = TextProcessor()
    dialogues = processor.extract_dialogues(sample_script)
    
    assert len(dialogues) > 0
    for character, line in dialogues:
        assert isinstance(character, str)
        assert isinstance(line, str)
        assert len(character) > 0
        assert len(line) > 0

def test_character_classifier_detects_gender():
    """Test that CharacterClassifier correctly identifies character gender."""
    classifier = CharacterClassifier()
    
    # Test female name detection
    sarah = Character(name="SARAH")
    sarah = classifier.classify_character(sarah)
    assert sarah.gender == "female"
    
    # Test male name detection
    john = Character(name="JOHN")
    john = classifier.classify_character(john)
    assert john.gender == "male"

def test_conversation_analyzer_finds_conversations(sample_script):
    """Test that ConversationAnalyzer identifies conversations correctly."""
    processor = TextProcessor()
    character_lines = processor.process_script(sample_script)
    
    classifier = CharacterClassifier()
    characters = {}
    for name, lines in character_lines.items():
        char = Character(name=name, lines=lines)
        char = classifier.classify_character(char)
        characters[name] = char
    
    analyzer = ConversationAnalyzer()
    conversations = analyzer.extract_conversations(character_lines, characters)
    
    print("Found conversations:", len(conversations))  # Debug print
    for conv in conversations:
        print("Participants:", [p.name for p in conv.participants])
        print("Dialogue:", conv.dialogue)
    
    assert len(conversations) > 0

def test_conversation_analyzer_finds_female_conversations(sample_script):
    """Test that ConversationAnalyzer identifies conversations between women."""
    processor = TextProcessor()
    character_lines = processor.process_script(sample_script)
    
    classifier = CharacterClassifier()
    characters = {}
    for name, lines in character_lines.items():
        char = Character(name=name, lines=lines)
        char = classifier.classify_character(char)
        characters[name] = char
    
    analyzer = ConversationAnalyzer()
    conversations = analyzer.extract_conversations(character_lines, characters)
    
    # Print debug information
    print("All conversations:", len(conversations))
    for conv in conversations:
        print("Participants:", [p.name for p in conv.participants])
        print("Gender:", [p.gender for p in conv.participants])
    
    # Verify conversations between women
    female_conversations = [
        conv for conv in conversations
        if all(char.gender == "female" for char in conv.participants)
        and len(conv.participants) >= 2
    ]
    
    assert len(female_conversations) > 0

def test_bechdel_analyzer_full_analysis(analyzer, sample_script):
    """Test full Bechdel test analysis on sample script."""
    result = analyzer.analyze_script(sample_script)
    
    # Print debug information
    print("Female characters:", [char.name for char in result.female_characters])
    if result.conversations:
        print("Conversations:", len(result.conversations))
        for conv in result.conversations:
            print("Participants:", [p.name for p in conv.participants])
    print("Failure reasons:", result.failure_reasons)
    
    assert isinstance(result, BechdelResult)
    assert result.passes_test is True
    assert len(result.female_characters) >= 2
    assert result.conversations is not None
    assert result.failure_reasons is None

def test_analyzer_with_script_file(analyzer):
    """Test analyzing script directly from file."""
    result = analyzer.analyze_script_file(str(SCRIPT_PATH))
    
    assert isinstance(result, BechdelResult)
    assert result.passes_test is True
    assert result.conversations is not None
