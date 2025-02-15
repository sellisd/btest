"""Module for finding and retrieving movie scripts."""

import os
import logging
from pathlib import Path
from typing import Optional, Dict
import requests
import pandas as pd

logger = logging.getLogger(__name__)

class ScriptFinder:
    """Handles retrieving movie scripts from Cornell Movie Dialog Corpus."""
    
    # Base URL for the dataset files
    DATASET_URL = "https://raw.githubusercontent.com/sellisd/btest/main/data/movie_data/"
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize ScriptFinder.
        
        Args:
            data_dir: Directory to store downloaded dataset files. 
                     Defaults to ~/btest_data if not specified.
        """
        if data_dir is None:
            data_dir = os.path.expanduser("~/btest_data")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache for loaded data
        self._movies_df: Optional[pd.DataFrame] = None
        self._dialogs: Optional[Dict] = None
        
    def _download_dataset(self) -> None:
        """Download dataset files if not already present."""
        files = ["movie_titles_metadata.txt", "movie_lines.txt"]
        
        for filename in files:
            file_path = self.data_dir / filename
            if not file_path.exists():
                logger.info(f"Downloading {filename}...")
                url = f"{self.DATASET_URL}{filename}"
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    file_path.write_text(response.text)
                except Exception as e:
                    logger.error(f"Failed to download {filename}: {e}")
                    raise
    
    def _load_data(self) -> None:
        """Load dataset into memory if not already loaded."""
        if self._movies_df is None or self._dialogs is None:
            try:
                self._download_dataset()
                
                # Load movie metadata
                movies_path = self.data_dir / "movie_titles_metadata.txt"
                self._movies_df = pd.read_csv(movies_path, sep=" \+\+\+ ", 
                                          names=["id", "title", "year", "rating", "votes", "genres"],
                                          engine="python")
                
                # Load movie lines
                lines_path = self.data_dir / "movie_lines.txt"
                self._dialogs = {}
                with open(lines_path, 'r', encoding='iso-8859-1') as f:
                    for line in f:
                        parts = line.strip().split(" +++$+++ ")
                        if len(parts) == 5:
                            movie_id = parts[2]
                            if movie_id not in self._dialogs:
                                self._dialogs[movie_id] = []
                            self._dialogs[movie_id].append({
                                'character': parts[1],
                                'text': parts[4]
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
        movie = self._movies_df[self._movies_df['title'].str.lower().str.contains(title)]
        
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
