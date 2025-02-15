"""Main entry point for the script scraping server."""

import logging
from src.api.server import start_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Start the script scraping server."""
    start_server()

if __name__ == "__main__":
    main()
