"""Tests for script finder module."""

from pathlib import Path
import pytest
from src.core.script_finder import ScriptFinder

MOCK_MOVIES_DATA = """m0 +++$+++ Movie1 +++$+++ 2020 +++$+++ 8.5 +++$+++ 1000 +++$+++ genre1|genre2
m1 +++$+++ Test Movie +++$+++ 2021 +++$+++ 7.5 +++$+++ 500 +++$+++ genre3
m2 +++$+++ Another Movie +++$+++ 2022 +++$+++ 6.5 +++$+++ 200 +++$+++ genre1"""

MOCK_LINES_DATA = """L1 +++$+++ CHAR1 +++$+++ m0 +++$+++ SCENE1 +++$+++ Hello there!
L2 +++$+++ CHAR2 +++$+++ m0 +++$+++ SCENE1 +++$+++ Hi!
L3 +++$+++ CHAR1 +++$+++ m1 +++$+++ SCENE1 +++$+++ Test dialog."""

MOCK_CONVERSATIONS_DATA = """c0 +++$+++ CHAR1 +++$+++ m0 +++$+++ ['L1', 'L2']
c1 +++$+++ CHAR1 +++$+++ m1 +++$+++ ['L3']"""


@pytest.fixture
def mock_data_dir(tmp_path):
    """Create a temporary directory for test data."""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir(parents=True, exist_ok=True)
    return str(test_dir)


@pytest.fixture
def mock_files(mock_data_dir):
    """Create mock dataset files."""
    data_dir = Path(mock_data_dir)

    # Create mock files
    (data_dir / "movie_titles_metadata.txt").write_text(MOCK_MOVIES_DATA)
    (data_dir / "movie_lines.txt").write_text(MOCK_LINES_DATA)
    (data_dir / "movie_conversations.txt").write_text(MOCK_CONVERSATIONS_DATA)

    return data_dir


def test_init_creates_data_dir(mock_data_dir):
    """Test that initializing creates the data directory."""
    finder = ScriptFinder(data_dir=mock_data_dir)
    assert finder.data_dir.exists()
    assert finder.data_dir == Path(mock_data_dir)


def test_find_script_exact_match(mock_files):
    """Test finding a script with exact title match."""
    finder = ScriptFinder(data_dir=str(mock_files))
    script = finder.find_script("Test Movie")

    assert script is not None
    assert "CHAR1: Test dialog." in script


def test_find_script_partial_match(mock_files):
    """Test finding a script with partial title match."""
    finder = ScriptFinder(data_dir=str(mock_files))
    script = finder.find_script("Movie1")

    assert script is not None
    assert "CHAR1: Hello there!" in script
    assert "CHAR2: Hi!" in script


def test_find_script_no_match(mock_files):
    """Test finding a script with no matching title."""
    finder = ScriptFinder(data_dir=str(mock_files))
    script = finder.find_script("Nonexistent Movie")
    assert script is None


def test_find_script_multiple_matches(mock_files):
    """Test finding a script when multiple titles match."""
    finder = ScriptFinder(data_dir=str(mock_files))
    # Should match both "Movie1" and "Another Movie", but pick Movie1 due to higher votes
    script = finder.find_script("Movie")

    assert script is not None
    assert "CHAR1: Hello there!" in script
    assert "CHAR2: Hi!" in script


def test_empty_data_directory(mock_data_dir):
    """Test behavior with empty data directory."""
    finder = ScriptFinder(data_dir=mock_data_dir)
    script = finder.find_script("Any Movie")
    assert script is None
