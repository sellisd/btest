"""Tests for script finder module."""

import os
from unittest.mock import patch, mock_open
import pytest
from src.core.script_finder import ScriptFinder

MOCK_MOVIES_DATA = """m0 +++ Movie1 +++ 2020 +++ 8.5 +++ 1000 +++ genre1|genre2
m1 +++ Test Movie +++ 2021 +++ 7.5 +++ 500 +++ genre3
m2 +++ Another Movie +++ 2022 +++ 6.5 +++ 200 +++ genre1"""

MOCK_LINES_DATA = """L1 +++$+++ CHAR1 +++$+++ m0 +++$+++ SCENE1 +++$+++ Hello there!
L2 +++$+++ CHAR2 +++$+++ m0 +++$+++ SCENE1 +++$+++ Hi!
L3 +++$+++ CHAR1 +++$+++ m1 +++$+++ SCENE1 +++$+++ Test dialog."""

@pytest.fixture
def mock_data_dir(tmp_path):
    """Create a temporary directory for test data."""
    return str(tmp_path / "test_data")

@pytest.fixture
def mock_finder(mock_data_dir):
    """Create ScriptFinder instance with mocked data directory."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.text = "mock data"
        finder = ScriptFinder(data_dir=mock_data_dir)
        return finder

def test_init_creates_data_dir(mock_data_dir):
    """Test that initializing creates the data directory."""
    ScriptFinder(data_dir=mock_data_dir)
    assert os.path.exists(mock_data_dir)

def test_find_script_exact_match(mock_finder):
    """Test finding a script with exact title match."""
    with patch('builtins.open', mock_open(read_data=MOCK_MOVIES_DATA)) as mock_movies_file, \
         patch('builtins.open', mock_open(read_data=MOCK_LINES_DATA)) as mock_lines_file:
        
        # Mock both file opens
        def mock_open_files(*args, **kwargs):
            if str(args[0]).endswith('movie_titles_metadata.txt'):
                return mock_movies_file.return_value
            return mock_lines_file.return_value
            
        with patch('builtins.open', mock_open_files):
            script = mock_finder.find_script("Test Movie")
            
            assert script is not None
            assert "CHAR1: Test dialog." in script

def test_find_script_partial_match(mock_finder):
    """Test finding a script with partial title match."""
    with patch('builtins.open', mock_open(read_data=MOCK_MOVIES_DATA)) as mock_movies_file, \
         patch('builtins.open', mock_open(read_data=MOCK_LINES_DATA)) as mock_lines_file:
        
        def mock_open_files(*args, **kwargs):
            if str(args[0]).endswith('movie_titles_metadata.txt'):
                return mock_movies_file.return_value
            return mock_lines_file.return_value
            
        with patch('builtins.open', mock_open_files):
            script = mock_finder.find_script("Movie1")
            
            assert script is not None
            assert "CHAR1: Hello there!" in script
            assert "CHAR2: Hi!" in script

def test_find_script_no_match(mock_finder):
    """Test finding a script with no matching title."""
    with patch('builtins.open', mock_open(read_data=MOCK_MOVIES_DATA)) as mock_movies_file, \
         patch('builtins.open', mock_open(read_data=MOCK_LINES_DATA)) as mock_lines_file:
        
        def mock_open_files(*args, **kwargs):
            if str(args[0]).endswith('movie_titles_metadata.txt'):
                return mock_movies_file.return_value
            return mock_lines_file.return_value
            
        with patch('builtins.open', mock_open_files):
            script = mock_finder.find_script("Nonexistent Movie")
            assert script is None

def test_find_script_multiple_matches(mock_finder):
    """Test finding a script when multiple titles match."""
    with patch('builtins.open', mock_open(read_data=MOCK_MOVIES_DATA)) as mock_movies_file, \
         patch('builtins.open', mock_open(read_data=MOCK_LINES_DATA)) as mock_lines_file:
        
        def mock_open_files(*args, **kwargs):
            if str(args[0]).endswith('movie_titles_metadata.txt'):
                return mock_movies_file.return_value
            return mock_lines_file.return_value
            
        with patch('builtins.open', mock_open_files):
            # Should match both "Movie1" and "Another Movie", but pick Movie1 due to higher votes
            script = mock_finder.find_script("Movie")
            
            assert script is not None
            assert "CHAR1: Hello there!" in script
            assert "CHAR2: Hi!" in script
