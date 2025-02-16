# Movie Script Scraping Service

A Python-based web service that fetches movie scripts from various online sources including IMSDB and Cinematheque.fr.

## Features

- Asynchronous script scraping from multiple sources
- Fallback mechanism when a source fails
- Local caching of retrieved scripts
- RESTful API with FastAPI
- Comprehensive test coverage
- Rate limiting to respect source websites
- Error handling and logging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/script-scraper.git
cd script-scraper
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Usage

### Starting the Server

Run the server with:
```bash
python src/main.py
```

The server will start on `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

### API Endpoints

#### Search for a Script

```http
GET /scripts/search?title={movie_title}
```

Example response:
```json
{
  "title": "The Matrix",
  "url": "https://imsdb.com/scripts/Matrix.html",
  "source": "IMSDB"
}
```

#### Get a Script

```http
GET /scripts/{movie_title}
```

Example response:
```json
{
  "title": "The Matrix",
  "script": "INT. COMPUTER SCREEN\nText flowing in tight corridors...",
  "source": "IMSDB",
  "url": "https://imsdb.com/scripts/Matrix.html"
}
```

#### Get Bechdel Test Score

```http
GET /movies/{movie_title}/bechdel-score
```

Example response:
```json
{
  "passes_test": true,
  "female_characters": ["Trinity", "Oracle", "Switch"],
  "num_female_conversations": 2,
  "failure_reasons": null
}
```

If the movie fails the test, the response might look like:
```json
{
  "passes_test": false,
  "female_characters": ["Sarah", "Maria"],
  "num_female_conversations": 0,
  "failure_reasons": ["No conversations between female characters found"]
}
```

### Error Responses

The API uses standard HTTP status codes:

- `200`: Success
- `404`: Script not found
- `503`: Scraping error (e.g., source website down)

Error response example:
```json
{
  "error": "Script scraping failed",
  "details": "Connection timeout"
}
```

## Development

### Running Tests

Run the test suite with:
```bash
pytest
```

### Project Structure

```
src/
  ├── api/
  │   ├── models.py      # Pydantic models
  │   └── server.py      # FastAPI server
  ├── core/
  │   └── scrapers/
  │       ├── base.py       # Base scraper interface
  │       ├── imsdb.py      # IMSDB implementation
  │       └── cinematheque.py # Cinematheque implementation
  └── main.py           # Entry point
tests/
  ├── test_api.py      # API tests
  ├── test_api_endpoints.py # API tests
  └── test_scrapers.py    # Scraper tests
```

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Write and test your changes
4. Commit your changes (`git commit -m 'feat: add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
