"""Test module for the Bechdel test analyzer."""

from pathlib import Path
from unittest.mock import patch, mock_open
import pytest

from src.core.text_processor import TextProcessor
from src.core.character import Character, CharacterClassifier
from src.core.conversation import ConversationAnalyzer
from src.core.analyzer import BechdelAnalyzer, BechdelResult
from src.core.script_finder import ScriptFinder

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

@pytest.fixture
def mock_movie_data():
    """Mock movie metadata for testing."""
    return """m0 +++$+++ Test Movie +++$+++ 2020 +++$+++ 8.5 +++$+++ 1000 +++$+++ genre1"""

@pytest.fixture
def mock_lines_data():
    """Mock movie lines for testing."""
    return """L1 +++$+++ SARAH +++$+++ m0 +++$+++ SCENE1 +++$+++ Hello Mary!
L2 +++$+++ MARY +++$+++ m0 +++$+++ SCENE1 +++$+++ Hi Sarah! Let's talk about science."""

@pytest.fixture
def mock_conversations_data():
    """Mock conversation data for testing."""
    return """c1 +++$+++ SARAH +++$+++ m0 +++$+++ ['L1', 'L2']"""

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
    
    assert len(conversations) > 0
    assert all(len(conv.participants) >= 2 for conv in conversations), "Each conversation should have at least 2 participants"
    assert all(conv.dialogue for conv in conversations), "Each conversation should have dialogue"

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
    
    # Verify conversations between women
    female_conversations = [
        conv for conv in conversations
        if all(char.gender == "female" for char in conv.participants)
        and len(conv.participants) >= 2
    ]
    
    assert len(female_conversations) > 0, "Should find at least one conversation between women"
    assert all(len(conv.participants) >= 2 for conv in female_conversations), "Female conversations should have at least 2 participants"

def test_bechdel_analyzer_full_analysis(analyzer, sample_script):
    """Test full Bechdel test analysis on sample script."""
    result = analyzer.analyze_script(sample_script)
    
    assert isinstance(result, BechdelResult)
    assert result.passes_test is True, "Sample script should pass Bechdel test"
    assert len(result.female_characters) >= 2, "Should identify at least 2 female characters"
    assert result.conversations is not None, "Should identify conversations"
    assert result.failure_reasons is None, "Passing test should have no failure reasons"

def test_analyzer_with_script_file(analyzer):
    """Test analyzing script directly from file."""
    result = analyzer.analyze_script_file(str(SCRIPT_PATH))
    
    assert isinstance(result, BechdelResult)
    assert result.passes_test is True
    assert result.conversations is not None

def test_analyze_movie_found(analyzer, mock_movie_data, mock_lines_data, mock_conversations_data):
    """Test analyzing movie by title when script is found."""
    with patch('builtins.open', mock_open(read_data=mock_movie_data)) as mock_movies_file, \
         patch('builtins.open', mock_open(read_data=mock_lines_data)) as mock_lines_file, \
         patch('builtins.open', mock_open(read_data=mock_conversations_data)) as mock_conv_file, \
         patch('requests.get') as mock_get:
             
        mock_get.return_value.text = "mock data"
        
        def mock_open_files(*args, **kwargs):
            path = str(args[0])
            if path.endswith('movie_titles_metadata.txt'):
                return mock_movies_file.return_value
            elif path.endswith('movie_conversations.txt'):
                return mock_conv_file.return_value
            return mock_lines_file.return_value
            
        with patch('builtins.open', mock_open_files):
            result = analyzer.analyze_movie("Test Movie")
            
            assert result is not None
            assert isinstance(result, BechdelResult)
            assert len(result.female_characters) == 2
            assert result.passes_test is True

def test_analyze_movie_not_found(analyzer, mock_movie_data, mock_lines_data):
    """Test analyzing movie by title when script is not found."""
    with patch('builtins.open', mock_open(read_data=mock_movie_data)) as mock_movies_file, \
         patch('builtins.open', mock_open(read_data=mock_lines_data)) as mock_lines_file, \
         patch('requests.get') as mock_get:
             
        mock_get.return_value.text = "mock data"
        
        def mock_open_files(*args, **kwargs):
            if str(args[0]).endswith('movie_titles_metadata.txt'):
                return mock_movies_file.return_value
            return mock_lines_file.return_value
            
        with patch('builtins.open', mock_open_files):
            result = analyzer.analyze_movie("Nonexistent Movie")
            assert result is None

@pytest.mark.parametrize("movie_title,should_pass", [
    ("crouching tiger, hidden dragon", True),   # Known to pass Bechdel test
    ("pitch black", True),       # Known to pass Bechdel test
    ("cast away", False),        # Known to fail Bechdel test
    ("gladiator", False),        # Known to fail Bechdel test
    ("high fidelity", False),    # Known to fail Bechdel test
])
def test_known_movie_validations(analyzer, movie_title, should_pass):
    """Test Bechdel test analysis on known movies with verified results."""
    result = analyzer.analyze_movie(movie_title)
    
    assert result is not None, f"Failed to find script for {movie_title}"
    
    assert result.passes_test == should_pass, \
        f"Expected {movie_title} to {'pass' if should_pass else 'fail'} but got opposite result"
    
    if should_pass:
        # For passing movies, verify we have:
        # 1. At least two female characters
        assert len(result.female_characters) >= 2, \
            f"Passing movie {movie_title} has fewer than 2 female characters"
        
        # 2. Some conversations between women
        female_convs = [
            conv for conv in result.conversations
            if all(char.gender == "female" for char in conv.participants)
            and len(conv.participants) >= 2
        ]
        assert len(female_convs) > 0, \
            f"Passing movie {movie_title} has no conversations between women"
    else:
        # For failing movies, verify we have failure reasons
        assert result.failure_reasons is not None and len(result.failure_reasons) > 0, \
            f"Failing movie {movie_title} has no failure reasons"
