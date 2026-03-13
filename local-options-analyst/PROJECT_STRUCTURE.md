# Project Structure and Module Documentation

## Complete File Structure

```
local-options-analyst/
├── README.md                          # Main project documentation
├── requirements.txt                   # Python dependencies
├── kiro-config.json                   # Configuration
├── main.py                            # Entry point
├── main.md                            # Entry point documentation
│
├── PHASE2_SUMMARY.md                  # Phase 2 implementation details
├── PHASE3_SUMMARY.md                  # Phase 3 AI prompts details
├── PHASE4_SUMMARY.md                  # Phase 4 simulation details
│
├── prompts/                           # AI prompt templates
│   ├── portfolio_prompt.txt           # Portfolio analysis prompt
│   ├── options_strategy_prompt.txt    # Strategy formulation prompt
│   └── sentiment_prompt.txt           # Sentiment analysis prompt
│
├── data/                              # Persistent data storage
│   ├── portfolio.json                 # Current positions by basket
│   ├── trades.json                    # Trade history
│   ├── pnl_history.json              # Daily PnL records
│   ├── simulation.json                # Simulation state (Phase 4)
│   └── market_data/
│       ├── nse_option_chain.json
│       └── daily_snapshots/           # Daily market snapshots
│
├── modules/                           # Core modules
│   ├── __init__.py
│   │
│   ├── ai/                            # AI integration
│   │   ├── __init__.py
│   │   ├── qwen_interface.py          # Ollama Qwen interface
│   │   ├── qwen_interface.md
│   │   ├── sentiment.py               # Sentiment analysis
│   │   └── sentiment.md
│   │
│   ├── analytics/                     # Analytics layer
│   │   ├── __init__.py
│   │   ├── portfolio.py               # Portfolio management
│   │   ├── portfolio.md
│   │   ├── options_strategy.py        # Strategy formulation
│   │   ├── options_strategy.md
│   │   ├── risk.py                    # Risk calculations
│   │   └── risk.md
│   │
│   ├── baskets/                       # Modular basket system (Phase 4)
│   │   ├── __init__.py
│   │   ├── base.py                    # Base classes and factory
│   │   └── base.md
│   │
│   ├── strategies/                    # Modular strategy system (Phase 4)
│   │   ├── __init__.py
│   │   ├── base.py                    # Base classes and factory
│   │   └── base.md
│   │
│   ├── simulation/                    # Simulation engine (Phase 4)
│   │   ├── __init__.py
│   │   ├── engine.py                  # Persistent simulation
│   │   └── engine.md
│   │
│   └── cli/                           # Command-line interface
│       ├── __init__.py
│       ├── commands.py                # CLI commands
│       └── commands.md
│
└── utils/                             # Utility functions
    ├── __init__.py
    ├── file_io.py                     # JSON/CSV operations
    ├── file_io.md
    ├── market_fetcher.py              # Market data fetching
    └── market_fetcher.md
```

## Module Import Paths

### AI Layer
```python
from modules.ai.qwen_interface import QwenInterface
from modules.ai.sentiment import SentimentAnalyzer
```

### Analytics Layer
```python
from modules.analytics.portfolio import Portfolio
from modules.analytics.options_strategy import OptionsStrategyAnalyzer
from modules.analytics.risk import RiskAnalyzer
```

### Baskets (Phase 4)
```python
from modules.baskets.base import BaseBasket, BasketFactory
from modules.baskets.base import IncomeBasket, HedgeBasket, SpeculationBasket
```

### Strategies (Phase 4)
```python
from modules.strategies.base import BaseStrategy, StrategyFactory
from modules.strategies.base import CreditSpreadStrategy, IronCondorStrategy
```

### Simulation (Phase 4)
```python
from modules.simulation.engine import SimulationEngine
```

### CLI
```python
from modules.cli.commands import CLI, run
```

### Utils
```python
from utils.file_io import read_json, write_json, read_prompt
from utils.market_fetcher import fetch_nse_data, get_mock_prices
```

## Python 3.x Compatibility

All code is compatible with **Python 3.8+**

### Features Used
- Type hints (optional, not enforced)
- f-strings for formatting
- Pathlib for file operations
- ABC (Abstract Base Classes) for interfaces
- JSON standard library
- CSV standard library
- datetime standard library

### No Python 2.x Dependencies
- All print statements use function syntax: `print()`
- All string operations use Python 3 syntax
- All file operations use context managers: `with open()`
- All imports use absolute paths

## Documentation Coverage

Every Python module has a corresponding `.md` file:

| Module | Documentation |
|--------|---------------|
| main.py | main.md |
| modules/ai/qwen_interface.py | modules/ai/qwen_interface.md |
| modules/ai/sentiment.py | modules/ai/sentiment.md |
| modules/analytics/portfolio.py | modules/analytics/portfolio.md |
| modules/analytics/options_strategy.py | modules/analytics/options_strategy.md |
| modules/analytics/risk.py | modules/analytics/risk.md |
| modules/baskets/base.py | modules/baskets/base.md |
| modules/strategies/base.py | modules/strategies/base.md |
| modules/simulation/engine.py | modules/simulation/engine.md |
| modules/cli/commands.py | modules/cli/commands.md |
| utils/file_io.py | utils/file_io.md |
| utils/market_fetcher.py | utils/market_fetcher.md |

## Dependencies

### Required
- **requests** (>=2.28.0) - HTTP requests for Ollama API

### Optional
- **ollama** - Must be installed separately (https://ollama.ai)
- **qwen2.5:3b** - Model must be pulled: `ollama pull qwen2.5:3b`

## Installation

```bash
# 1. Clone/navigate to project
cd local-options-analyst

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Ollama
# Visit https://ollama.ai and follow installation instructions

# 4. Pull model
ollama pull qwen2.5:3b

# 5. Verify installation
python main.py --help
```

## Testing Imports

```python
# Test all imports
python -c "
from modules.ai.qwen_interface import QwenInterface
from modules.ai.sentiment import SentimentAnalyzer
from modules.analytics.portfolio import Portfolio
from modules.analytics.options_strategy import OptionsStrategyAnalyzer
from modules.analytics.risk import RiskAnalyzer
from modules.baskets.base import BasketFactory
from modules.strategies.base import StrategyFactory
from modules.simulation.engine import SimulationEngine
from modules.cli.commands import CLI
from utils.file_io import read_json, write_json
from utils.market_fetcher import get_mock_prices
print('All imports successful!')
"
```

## File Paths

All file paths use `pathlib.Path` for cross-platform compatibility:

```python
from pathlib import Path

# Relative to module
data_dir = Path(__file__).parent.parent / 'data'

# Absolute
project_root = Path('/home/amit/Desktop/coding-asistant/local-options-analyst')
```

## Modular Design Principles

1. **Separation of Concerns**: Each module has single responsibility
2. **Abstract Base Classes**: Enforce interfaces for extensibility
3. **Factory Pattern**: Consistent object creation
4. **Dependency Injection**: Pass dependencies to constructors
5. **Configuration**: External config files (JSON)
6. **Documentation**: Every module documented with examples

## Extension Points

### Add New Basket Type
1. Create class inheriting from `BaseBasket`
2. Implement `validate_position()` and `get_target_allocation()`
3. Register with `BasketFactory.register_basket_type()`

### Add New Strategy
1. Create class inheriting from `BaseStrategy`
2. Implement `generate_signals()` and `get_risk_parameters()`
3. Register with `StrategyFactory.register_strategy_type()`

### Add New Asset Type
1. Extend position structure in `portfolio.json`
2. Update `Portfolio` class validation if needed
3. Update risk calculations in `RiskAnalyzer`

## Best Practices

1. **Always use absolute imports** from project root
2. **Use pathlib.Path** for file operations
3. **Document all public methods** with docstrings
4. **Validate inputs** in all public methods
5. **Return consistent data structures** (dicts with known keys)
6. **Log errors** instead of silent failures
7. **Use type hints** for clarity (optional but recommended)

## Troubleshooting

### Import Errors
- Ensure you're running from project root: `cd local-options-analyst`
- Check Python path: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`

### Module Not Found
- Verify all `__init__.py` files exist
- Check file paths are correct
- Ensure no circular imports

### Ollama Connection Errors
- Verify Ollama is running: `ollama list`
- Check default port: `http://localhost:11434`
- Test connection: `curl http://localhost:11434/api/tags`
