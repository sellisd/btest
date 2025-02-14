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

# Analyze script from file
result = analyzer.analyze_script_file("path/to/script.txt")

# Print results
print(f"Passed Bechdel test: {result.passes_test}")
print(f"Female characters: {[char.name for char in result.female_characters]}")
if not result.passes_test:
    print(f"Failure reasons: {result.failure_reasons}")
```

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

LLM features can be customized through environment variables:
- `OLLAMA_MODEL`: Choose a different model (default: "llama2")
- `OLLAMA_HOST`: Connect to a remote Ollama instance

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

# Run tests
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your chosen license]
