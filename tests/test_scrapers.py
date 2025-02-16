import pytest
from src.core.scrapers import IMSDBScraper


@pytest.mark.asyncio
async def test_imsdb_real_scraping():
    """Integration test for IMSDB scraper with real HTTP requests.

    Tests both the search functionality and script content retrieval.
    Verifies the presence of expected script formatting and content markers.
    """
    async with IMSDBScraper() as scraper:  # Use async context manager
        try:
            # Search for a known movie script
            search_result = await scraper.search_script("The Matrix")

            # Verify search results
            assert search_result is not None, "Search result should not be None"
            assert search_result["source"] == "IMSDB", "Source should be IMSDB"
            assert "Matrix" in search_result["title"], "Title should contain 'Matrix'"
            assert "url" in search_result, "Search result should contain URL"

            # Get the actual script content
            script_content = await scraper.get_script(search_result["url"])
            # Verify basic script content structure
            assert isinstance(script_content, str), "Script content should be string"
            assert len(script_content) > 1000, "Script should be substantial in length"

            # Verify script formatting markers
            script_markers = ["INT.", "EXT.", "FADE IN:", "CUT TO:"]
            assert any(marker in script_content for marker in script_markers), (
                "Script should contain standard screenplay formatting markers"
            )

        except Exception as e:
            pytest.fail(f"Test failed with exception: {str(e)}")


# @pytest.mark.integration
# @pytest.mark.asyncio
# async def test_imsdb_script_encoding():
#     """Test handling of different character encodings in script content."""
#     async with IMSDBScraper() as scraper:
#         try:
#             # Choose a script known to have special characters
#             search_result = await scraper.search_script("Amélie")
#             script_content = await scraper.get_script(search_result["url"])

#             # Verify content can be properly decoded
#             assert isinstance(script_content, str)
#             assert len(script_content) > 0

#         except Exception as e:
#             pytest.fail(f"Test failed with exception: {str(e)}")
