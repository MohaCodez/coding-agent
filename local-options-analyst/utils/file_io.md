# file_io.py

## Purpose
Utility functions for reading/writing JSON data and loading prompt templates.

## Functions

### read_json(filepath)
Read JSON file and return parsed data.

**Inputs:**
- `filepath`: Path to JSON file

**Outputs:**
- Parsed JSON data (dict/list)

**Example:**
```python
from utils.file_io import read_json

portfolio = read_json('data/portfolio.json')
print(portfolio['positions'])
```

### write_json(filepath, data)
Write data to JSON file with formatting.

**Inputs:**
- `filepath`: Path to JSON file
- `data`: Data to write (dict/list)

**Outputs:**
- None (writes to file)

**Example:**
```python
from utils.file_io import write_json

data = {"positions": [], "cash": 100000}
write_json('data/portfolio.json', data)
```

### read_prompt(prompt_name)
Load prompt template from prompts/ directory.

**Inputs:**
- `prompt_name`: Name without .txt extension (e.g., "portfolio_prompt")

**Outputs:**
- Prompt template string

**Example:**
```python
from utils.file_io import read_prompt

template = read_prompt('options_strategy_prompt')
prompt = template.format(
    market_view="bullish",
    underlying="NIFTY",
    current_price=21500,
    volatility="medium"
)
```

## Use Cases
- Persistent storage of portfolio, trades, PnL
- Loading AI prompt templates
- Configuration management
- Data backup and recovery
