# Automated Bechdel Test Analyzer

A Python package for automated Bechdel test analysis of movie scripts.

## Features

- Analyzes movie scripts for Bechdel test compliance
- Detects character gender using name analysis and context
- Identifies conversations between female characters
- Analyzes conversation topics using rule-based and LLM methods
- Provides detailed results with failure reasons
- Local LLM support through Ollama integration

## Installation

```bash
pip install btest
```

## Requirements

- Python 3.8+
- [Ollama](https://github.com/ollama/ollama) (optional, for LLM features)

## Quick Start

```python
from btest.core.analyzer import BechdelAnalyzer

# Create analyzer instance
analyzer = BechdelAnalyzer()

# Analyze a movie directly by title
result = analyzer.analyze_movie("The Matrix")
if result:
    print(f"Passed Bechdel test: {result.passes_test}")
    print(f"Female characters: {[char.name for char in result.female_characters]}")
    if not result.passes_test:
        print(f"Failure reasons: {result.failure_reasons}")
else:
    print("Movie script not found")

# Or analyze a local script file
result = analyzer.analyze_script_file("path/to/script.txt")

# Print results
print(f"Passed Bechdel test: {result.passes_test}")
print(f"Female characters: {[char.name for char in result.female_characters]}")
if not result.passes_test:
    print(f"Failure reasons: {result.failure_reasons}")
```

## Movie Script Sources

The package includes a built-in movie script database from the Cornell Movie Dialog Corpus. Scripts are automatically downloaded and cached locally when needed.

To analyze a movie:
1. Search for a movie by title using `analyze_movie()`
2. The package will download and parse the script if available
3. Results are cached locally for future use

If a script isn't found in the database, you can still analyze a local script file using `analyze_script_file()`.

## Using LLM Features

The package can use Ollama for improved analysis:

1. Install Ollama following [their instructions](https://ollama.ai/download)
2. Start the Ollama service
3. Pull the required model (default is llama2):
   ```bash
   ollama pull llama2
   ```

The LLM features provide:
- More accurate gender detection for ambiguous names
- Better conversation topic analysis
- Validation of Bechdel test results

If Ollama is not available, the package falls back to rule-based analysis.

## Configuration

### LLM Configuration
The package's LLM features can be customized through environment variables:
- `OLLAMA_MODEL`: Choose a different model (default: "llama2")
- `OLLAMA_HOST`: Connect to a remote Ollama instance (optional)
- `OLLAMA_TIMEOUT`: Set request timeout in seconds (default: 30)
- `OLLAMA_CACHE_SIZE`: Set LLM response cache size (default: 128)

### Logging Configuration
Logging behavior can be customized through environment variables:
- `LOG_LEVEL`: Set logging level (default: "INFO")
- `LOG_FORMAT`: Customize log message format (default: "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

### Development Configuration
When developing or contributing:
1. Create a `.env` file in the project root:
   ```bash
   OLLAMA_MODEL=llama2
   OLLAMA_HOST=localhost:11434  # Optional
   OLLAMA_TIMEOUT=30
   OLLAMA_CACHE_SIZE=128
   LOG_LEVEL=DEBUG  # Use DEBUG for development
   ```
2. The package will automatically load these settings

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/btest.git
cd btest

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest --cov=src/core tests/

# Run specific test files
pytest tests/test_analyzer.py
pytest tests/test_script_finder.py

# Run tests with logging
pytest -v --log-cli-level=DEBUG
```

### Project Structure

```
btest/
├── src/
│   └── core/
│       ├── __init__.py
│       ├── analyzer.py      # Main Bechdel test analyzer
│       ├── character.py     # Character classification
│       ├── config.py        # Configuration management
│       ├── conversation.py  # Conversation analysis
│       ├── exceptions.py    # Custom exceptions
│       ├── llm_helper.py    # LLM integration
│       ├── logger.py        # Logging configuration
│       ├── script_finder.py # Script discovery
│       └── text_processor.py # Text processing utilities
├── tests/
│   ├── test_analyzer.py
│   ├── test_config.py
│   ├── test_exceptions.py
│   └── test_script_finder.py
└── scripts/
    └── analyze_movie.py    # CLI script example
```

### Error Handling

The package uses a custom exception hierarchy for clear error handling:

```python
BtestError
├── LLMError          # LLM-related issues
├── ScriptError      # Base for script issues
│   ├── ScriptNotFoundError
│   └── ScriptParseError
├── ConfigurationError # Config issues
├── ValidationError   # Validation failures
├── ConversationError # Conversation analysis issues
└── CharacterError   # Character detection issues
```

Example error handling:
```python
from btest.core.exceptions import ScriptNotFoundError

try:
    result = analyzer.analyze_movie("Non-existent Movie")
except ScriptNotFoundError as e:
    print(f"Movie script not found: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your chosen license]
