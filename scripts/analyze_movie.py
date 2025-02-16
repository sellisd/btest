#!/usr/bin/env python3
"""Script to analyze any movie script for Bechdel test compliance."""

import argparse
import asyncio
import aiohttp
from typing import List, Optional, Dict, Any
from src.core.analyzer import BechdelAnalyzer
from src.core.conversation import Conversation

API_BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'-' * 80}")
    print(f"{title}")
    print(f"{'-' * 80}")


def print_conversations(
    conversations: List[Conversation], show_only_female: bool = False
):
    """Print formatted conversations."""
    for i, conv in enumerate(conversations, 1):
        if show_only_female and not all(
            char.gender == "female" for char in conv.participants
        ):
            continue

        print(f"\nConversation {i}:")
        print("Participants:", ", ".join(char.name for char in conv.participants))
        print("Dialog:")
        print(conv.dialogue)
        print("-" * 40)


async def get_script(title: str) -> Optional[Dict[str, Any]]:
    """Get script from API.

    Args:
        title: Movie title to search for

    Returns:
        Script data if found, None otherwise
    """
    async with aiohttp.ClientSession() as session:
        try:
            # First search for the script
            async with session.get(
                f"{API_BASE_URL}/scripts/search", params={"title": title}
            ) as resp:
                if resp.status != 200:
                    return None
                await resp.json()

            # Then get the full script
            async with session.get(f"{API_BASE_URL}/scripts/{title}") as resp:
                if resp.status != 200:
                    return None
                return await resp.json()
        except aiohttp.ClientError:
            print("Error: Could not connect to script API server. Is it running?")
            return None


async def analyze_movie(analyzer: BechdelAnalyzer, title: str):
    """Analyze a movie script and print results.

    Args:
        analyzer: BechdelAnalyzer instance
        title: Movie title to analyze
    """
    # Get script from API
    script_data = await get_script(title)
    if not script_data:
        print(f"No script found for: {title}")
        return

    # Analyze the script
    result = analyzer.analyze_movie(script_data["script"])
    if not result:
        print("Could not analyze script")
        return

    # Print sample of raw dialogs
    print_section("Sample of Raw Dialogs (First 10 lines)")
    for line in script_data["script"].split("\n")[:10]:
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
            conv
            for conv in result.conversations
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


async def main_async():
    """Async main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze a movie script for Bechdel test."
    )
    parser.add_argument("title", help="Title of the movie to analyze")
    args = parser.parse_args()

    print_section(f"Bechdel Test Analysis: {args.title}")

    analyzer = BechdelAnalyzer()
    await analyze_movie(analyzer, args.title)


def main():
    """Main entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
