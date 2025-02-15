"""Module for finding and retrieving movie scripts."""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, List
import pandas as pd

logger = logging.getLogger(__name__)

class ScriptFinder:
    """Handles retrieving movie scripts from Cornell Movie Dialog Corpus."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize ScriptFinder.
        
        Args:
            data_dir: Directory to store downloaded dataset files. 
                     Defaults to local Cornell corpus if not specified.
        """
        if data_dir is None:
            data_dir = "data/cornell_data/cornell_movie_dialogs_corpus/cornell movie-dialogs corpus"
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Cornell Movie Dialog Corpus not found at {self.data_dir}")
        
        # Cache for loaded data
        self._movies_df: Optional[pd.DataFrame] = None
        self._dialogs: Optional[Dict] = None
        self._lines: Optional[Dict] = None
        
    def _load_data(self) -> None:
        """Load dataset into memory if not already loaded."""
        if self._movies_df is None or self._dialogs is None:
            try:
                # Load movie metadata
                movies_path = self.data_dir / "movie_titles_metadata.txt"
                self._movies_df = pd.read_csv(movies_path, sep=" \\+\\+\\+\\$\\+\\+\\+ ", 
                                          names=["id", "title", "year", "rating", "votes", "genres"],
                                          engine="python",
                                          encoding='iso-8859-1',
                                          dtype={"id": str, "title": str, "year": str, 
                                                "rating": float, "votes": float, "genres": str})
                
                # Load movie lines into a dictionary for quick lookup
                lines_path = self.data_dir / "movie_lines.txt"
                self._lines = {}
                with open(lines_path, 'r', encoding='iso-8859-1') as f:
                    for line in f:
                        parts = line.strip().split(" +++$+++ ")
                        if len(parts) == 5:
                            line_id, character, movie_id, _, text = parts
                            self._lines[line_id] = {
                                'character': character,
                                'movie_id': movie_id,
                                'text': text
                            }
                
                # Load movie conversations which define the line ordering
                conversations_path = self.data_dir / "movie_conversations.txt"
                self._dialogs = {}
                with open(conversations_path, 'r', encoding='iso-8859-1') as f:
                    for conversation in f:
                        parts = conversation.strip().split(" +++$+++ ")
                        if len(parts) == 4:
                            # Extract line IDs from conversation
                            movie_id = parts[2]
                            line_ids = eval(parts[3])  # Convert string list to actual list
                            
                            if movie_id not in self._dialogs:
                                self._dialogs[movie_id] = []
                            
                            # Add each line in the conversation
                            for line_id in line_ids:
                                if line_id in self._lines:
                                    line = self._lines[line_id]
                                    self._dialogs[movie_id].append({
                                        'character': line['character'],
                                        'text': line['text']
                                    })
                            
            except Exception as e:
                logger.error(f"Failed to load dataset: {e}")
                raise
    
    def find_script(self, title: str) -> Optional[str]:
        """Find and return movie script by title.
        
        Args:
            title: Movie title to search for.
            
        Returns:
            Formatted script text if found, None otherwise.
        """
        self._load_data()
        
        # Search for movie
        title = title.lower()
        # Fill NaN values and convert to string before searching
        movie = self._movies_df[self._movies_df['title'].fillna('').astype(str).str.lower().str.contains(title)]
        
        if len(movie) == 0:
            logger.warning(f"No movie found matching title: {title}")
            return None
            
        if len(movie) > 1:
            # If multiple matches, use the one with most votes
            movie = movie.sort_values('votes', ascending=False).iloc[0]
        else:
            movie = movie.iloc[0]
            
        movie_id = movie['id']
        
        if movie_id not in self._dialogs:
            logger.warning(f"No dialog found for movie: {title}")
            return None
            
        # Format dialog into script
        script_lines = []
        for dialog in self._dialogs[movie_id]:
            script_lines.append(f"{dialog['character']}: {dialog['text']}")
            
        return "\n".join(script_lines)
