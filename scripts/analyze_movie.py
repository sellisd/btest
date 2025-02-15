#!/usr/bin/env python3
"""Script to analyze any movie script for Bechdel test compliance."""

import argparse
from difflib import SequenceMatcher
from typing import List, Optional, Tuple
from src.core.analyzer import BechdelAnalyzer
from src.core.character import Character
from src.core.conversation import Conversation
from src.core.script_finder import ScriptFinder

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'-' * 80}")
    print(f"{title}")
    print(f"{'-' * 80}")

def print_conversations(conversations: List[Conversation], show_only_female: bool = False):
    """Print formatted conversations."""
    for i, conv in enumerate(conversations, 1):
        if show_only_female and not all(char.gender == "female" for char in conv.participants):
            continue
            
        print(f"\nConversation {i}:")
        print("Participants:", ", ".join(char.name for char in conv.participants))
        print("Dialog:")
        print(conv.dialogue)
        print("-" * 40)

def find_best_match(title: str, movies_df) -> Tuple[Optional[str], float]:
    """Find the best matching title using fuzzy string matching.
    
    Args:
        title: Title to search for
        movies_df: DataFrame containing movie information
        
    Returns:
        Tuple of (best matching title or None, match ratio)
    """
    best_match = None
    best_ratio = 0
    
    for available in movies_df['title']:
        if not isinstance(available, str):
            continue
        ratio = SequenceMatcher(None, title.lower(), available.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = available
            
    return best_match, best_ratio

def analyze_movie(analyzer: BechdelAnalyzer, finder: ScriptFinder, title: str):
    """Analyze a movie script and print results.
    
    Args:
        analyzer: BechdelAnalyzer instance
        finder: ScriptFinder instance
        title: Movie title to analyze
    """
    # Try exact match first
    result = analyzer.analyze_movie(title)
    
    if result is None:
        print("\nExact title match not found, trying fuzzy search...")
        finder._load_data()  # Ensure data is loaded
        best_match, ratio = find_best_match(title, finder._movies_df)
        
        if best_match and ratio > 0.6:  # 60% similarity threshold
            print(f"Using closest match: '{best_match}' (similarity: {ratio:.1%})")
            result = analyzer.analyze_movie(best_match)
        else:
            print("No suitable movie match found.")
            print("\nTop 5 closest matches:")
            matches = []
            for available in finder._movies_df['title']:
                if not isinstance(available, str):
                    continue
                ratio = SequenceMatcher(None, title.lower(), available.lower()).ratio()
                matches.append((available, ratio))
            
            for title, ratio in sorted(matches, key=lambda x: x[1], reverse=True)[:5]:
                print(f"- '{title}' (similarity: {ratio:.1%})")
            return
    
    # Print sample of raw dialogs
    print_section("Sample of Raw Dialogs (First 10 lines)")
    script = finder.find_script(title)
    if script:
        for line in script.split('\n')[:10]:
            print(line)
    
    # Print basic result
    print(f"\nBechdel Test Result: {'PASS' if result.passes_test else 'FAIL'}")
    
    # Print all characters and their genders
    print_section("All Characters")
    all_chars = set()
    for conv in result.conversations or []:
        for char in conv.participants:
            all_chars.add(char)
    
    for char in sorted(all_chars, key=lambda x: x.name):
        print(f"- {char.name} (Gender: {char.gender})")
    
    # Print female characters
    print_section("Female Characters")
    for char in result.female_characters:
        print(f"- {char.name}")
    
    if result.conversations:
        # Print conversations between women
        print_section("Conversations Between Female Characters")
        female_conversations = [
            conv for conv in result.conversations
            if all(char.gender == "female" for char in conv.participants)
            and len(conv.participants) >= 2
        ]
        
        if female_conversations:
            print_conversations(female_conversations)
        else:
            print("No conversations between female characters found.")
    
    # Print failure reasons if any
    if not result.passes_test and result.failure_reasons:
        print_section("Failure Reasons")
        for reason in result.failure_reasons:
            print(f"- {reason}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Analyze a movie script for Bechdel test.')
    parser.add_argument('title', help='Title of the movie to analyze')
    args = parser.parse_args()
    
    print_section(f"Bechdel Test Analysis: {args.title}")
    
    analyzer = BechdelAnalyzer()
    finder = ScriptFinder()
    
    analyze_movie(analyzer, finder, args.title)

if __name__ == "__main__":
    main()
