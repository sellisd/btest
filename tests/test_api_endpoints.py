"""End-to-end tests for the movie script API endpoints."""

import pytest
from fastapi.testclient import TestClient
import asyncio

from src.api.server import app
from src.core.analyzer import BechdelAnalyzer

MOVIE_TITLE = "The Matrix"  # Using a known movie for consistent testing

@pytest.fixture
def test_client():
    """Configure FastAPI app for testing."""
    return TestClient(app)

def test_bechdel_score_endpoint(test_client):
    """Test the Bechdel score endpoint."""
    with test_client as client:
        # Get Bechdel score
        response = client.get(f"/movies/{MOVIE_TITLE}/bechdel-score")
        assert response.status_code == 200, f"Bechdel score request failed: {response.text}"
        result = response.json()

        # Verify response structure
        assert "passes_test" in result, "Result missing passes_test field"
        assert isinstance(result["passes_test"], bool), "passes_test should be boolean"
        assert "female_characters" in result, "Result missing female_characters"
        assert isinstance(result["female_characters"], list), "female_characters should be list"
        assert "num_female_conversations" in result, "Result missing num_female_conversations"
        assert isinstance(result["num_female_conversations"], int), "num_female_conversations should be integer"
        
        # Log results
        print(f"\nBechdel Score Results for {MOVIE_TITLE}:")
        print(f"Passes test: {result['passes_test']}")
        print(f"Number of female characters: {len(result['female_characters'])}")
        print(f"Number of female conversations: {result['num_female_conversations']}")
        if result.get("failure_reasons"):
            print("Failure reasons:")
            for reason in result["failure_reasons"]:
                print(f"- {reason}")

def test_script_search_and_analyze(test_client):
    """Test the end-to-end flow of searching for a script and analyzing it."""
    with test_client as client:
        # Step 1: Search for the script
        response = client.get("/scripts/search", params={"title": MOVIE_TITLE})
        assert response.status_code == 200, f"Script search failed: {response.text}"
        search_result = response.json()

        # Verify search response structure
        assert "title" in search_result, "Search result missing title"
        assert "url" in search_result, "Search result missing URL"
        assert "source" in search_result, "Search result missing source"

        # Step 2: Get the full script
        response = client.get(f"/scripts/{MOVIE_TITLE}")
        assert response.status_code == 200, f"Script retrieval failed: {response.text}"
        script_result = response.json()

        # Verify script response structure
        assert "title" in script_result, "Script missing title"
        assert "script" in script_result, "Script missing content"
        assert isinstance(script_result["script"], str), "Script content should be string"
        assert len(script_result["script"]) > 1000, "Script seems too short"

        # Step 3: Analyze script for Bechdel test
        analyzer = BechdelAnalyzer()
        analysis = analyzer.analyze_script(script_result["script"])

        # Verify analysis result
        assert analysis is not None, "Analysis should not be None"
        assert hasattr(analysis, "passes_test"), "Analysis missing passes_test field"
        assert isinstance(analysis.passes_test, bool), "passes_test should be boolean"
        assert hasattr(analysis, "female_characters"), "Analysis missing female_characters"
        assert isinstance(analysis.female_characters, list), "female_characters should be list"

        # Log analysis results
        print(f"\nBechdel Test Results for {MOVIE_TITLE}:")
        print(f"Passes test: {analysis.passes_test}")
        print(f"Number of female characters: {len(analysis.female_characters)}")
        if hasattr(analysis, "failure_reasons") and analysis.failure_reasons:
            print("Failure reasons:")
            for reason in analysis.failure_reasons:
                print(f"- {reason}")

if __name__ == "__main__":
    asyncio.run(test_script_search_and_analyze(None))
