#!/usr/bin/env python3
"""Script to list available movies in the Cornell Movie Dialog Corpus."""

from core.script_finder import ScriptFinder
import pandas as pd


def main():
    """List available movies sorted by popularity."""
    # Set display options for pandas
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    print("Loading movie database...")
    finder = ScriptFinder()
    # This will download and load the dataset
    finder._load_data()
    movies = finder._movies_df

    # Sort by number of votes (popularity)
    movies_sorted = movies.sort_values("votes", ascending=False)

    print("\nAvailable movies (sorted by popularity):")
    print("-" * 80)
    print(f"{'Title':<50} {'Year':<6} {'Rating':<8} {'Votes':<8}")
    print("-" * 80)

    for _, movie in movies_sorted.iterrows():
        title = str(movie["title"]) if pd.notna(movie["title"]) else "Unknown"
        year = str(movie["year"]) if pd.notna(movie["year"]) else "N/A"
        rating = f"{movie['rating']:.1f}" if pd.notna(movie["rating"]) else "N/A"
        votes = str(int(movie["votes"])) if pd.notna(movie["votes"]) else "0"

        print(
            f"{title[:47] + '...' if len(title) > 47 else title:<50} "
            f"{year:<6} "
            f"{rating:<8} "
            f"{votes:<8}"
        )


if __name__ == "__main__":
    main()
