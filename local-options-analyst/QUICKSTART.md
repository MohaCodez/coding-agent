# Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Navigate to project
cd local-options-analyst

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Ollama
# Visit https://ollama.ai and follow instructions for your OS

# 4. Pull AI model
ollama pull qwen2.5:3b

# 5. Verify
python main.py --help
```

## Basic Usage (10 minutes)

### 1. Add Positions
```bash
# Income basket
python main.py add_trade income NIFTY24MAR21000CE 50 150.5 long
python main.py add_trade income NIFTY24MAR21200CE 50 120.0 short

# Hedge basket
python main.py add_trade hedge NIFTY24MAR20500PE 25 80.0 long
```

### 2. Analyze Portfolio
```bash
python main.py analyze
# Shows: valuation, allocations, Greeks, AI insights
```

### 3. View Report
```bash
python main.py report
# Complete portfolio summary with PnL
```

## Simulation Workflow (15 minutes)

### Start Simulation
```bash
python main.py sim_start
```

### Run Multiple Days
```bash
# Day 1
python main.py sim_run_day

# Day 2
python main.py sim_run_day

# Day 3
python main.py sim_run_day
```

### Execute Suggested Trades
```bash
python main.py sim_execute_trade income NIFTY24MAR21300CE 50 110.0 short
```

### Log Hedging Actions
```bash
python main.py sim_log_hedge "Rolled protective put to next expiry"
```

### View Summary
```bash
python main.py sim_summary
# Shows cumulative income, basket breakdown, recent days
```

### Stop Simulation
```bash
python main.py sim_stop
```

## Advanced Features

### Income Strategy Formulation
```bash
python main.py formulate_income \
  --target 15000 \
  --view bullish \
  --underlying NIFTY \
  --price 21500 \
  --volatility medium \
  --risk medium
```

### Sentiment Analysis
```bash
# Text format
python main.py sentiment "RBI maintains dovish stance"

# JSON format (specific underlying)
python main.py sentiment "FII selling continues" --json --underlying NIFTY

# Full JSON (all underlyings)
python main.py sentiment "Market rally" --full
```

### Strategy Suggestions
```bash
python main.py strategy \
  --view bearish \
  --underlying BANKNIFTY \
  --price 45000 \
  --volatility high
```

## Common Commands Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `add_trade` | Add position | `python main.py add_trade income NIFTY24MAR21000CE 50 150.5 long` |
| `analyze` | AI analysis | `python main.py analyze` |
| `report` | Portfolio summary | `python main.py report` |
| `formulate_income` | Income strategies | `python main.py formulate_income --target 15000 --view bullish --underlying NIFTY --price 21500` |
| `sentiment` | Sentiment analysis | `python main.py sentiment "RBI dovish" --json` |
| `sim_start` | Start simulation | `python main.py sim_start` |
| `sim_run_day` | Run one day | `python main.py sim_run_day` |
| `sim_summary` | View results | `python main.py sim_summary` |
| `sim_stop` | Stop simulation | `python main.py sim_stop` |

## File Locations

### Data Files
- Portfolio: `data/portfolio.json`
- Trades: `data/trades.json`
- PnL History: `data/pnl_history.json`
- Simulation: `data/simulation.json`
- Snapshots: `data/market_data/daily_snapshots/`

### Configuration
- Kiro Config: `kiro-config.json`
- AI Prompts: `prompts/*.txt`

### Documentation
- Main README: `README.md`
- Phase Summaries: `PHASE2_SUMMARY.md`, `PHASE3_SUMMARY.md`, `PHASE4_SUMMARY.md`
- Module Docs: `modules/**/*.md`
- Project Structure: `PROJECT_STRUCTURE.md`
- Verification: `VERIFICATION.md`

## Extending the System

### Add New Basket Type
```python
# In your custom module
from modules.baskets.base import BaseBasket, BasketFactory

class ArbitrageBasket(BaseBasket):
    def validate_position(self, symbol, quantity, price, position_type):
        return True  # Your validation logic
    
    def get_target_allocation(self):
        return 0.15  # 15% allocation

# Register
BasketFactory.register_basket_type("arbitrage", ArbitrageBasket)

# Use
basket = BasketFactory.create_basket("arbitrage", "my_arb")
```

### Add New Strategy
```python
# In your custom module
from modules.strategies.base import BaseStrategy, StrategyFactory

class ButterflyStrategy(BaseStrategy):
    def generate_signals(self, market_data, portfolio_state):
        return {
            "strategy": "butterfly",
            "signals": [...]
        }
    
    def get_risk_parameters(self):
        return {"max_loss": 3000}

# Register
StrategyFactory.register_strategy_type("butterfly", ButterflyStrategy)

# Use
strategy = StrategyFactory.create_strategy("butterfly", "my_butterfly")
```

## Troubleshooting

### Ollama Not Running
```bash
# Check if Ollama is running
ollama list

# Start Ollama (if needed)
ollama serve
```

### Import Errors
```bash
# Ensure you're in project root
cd local-options-analyst

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Model Not Found
```bash
# Pull the model
ollama pull qwen2.5:3b

# Verify
ollama list
```

### Data File Errors
```bash
# Check data files exist
ls data/*.json

# If missing, they'll be created on first run
```

## Complete Example Workflow

```bash
# 1. Setup
cd local-options-analyst
pip install -r requirements.txt
ollama pull qwen2.5:3b

# 2. Add initial positions
python main.py add_trade income NIFTY24MAR21000CE 50 150.5 long
python main.py add_trade income NIFTY24MAR21200CE 50 120.0 short
python main.py add_trade hedge NIFTY24MAR20500PE 25 80.0 long

# 3. Analyze
python main.py analyze

# 4. Start simulation
python main.py sim_start

# 5. Run 5 days
for i in {1..5}; do
  python main.py sim_run_day
  sleep 1
done

# 6. View results
python main.py sim_summary

# 7. Get sentiment
python main.py sentiment "RBI maintains dovish stance" --full

# 8. Formulate new strategy
python main.py formulate_income --target 20000 --view neutral --underlying NIFTY --price 21500

# 9. Stop simulation
python main.py sim_stop

# 10. Final report
python main.py report
```

## Help Commands

```bash
# General help
python main.py --help

# Command-specific help
python main.py add_trade --help
python main.py formulate_income --help
python main.py sentiment --help
python main.py sim_start --help
```

## Documentation

- **README.md** - Main project overview
- **PROJECT_STRUCTURE.md** - Complete file structure and imports
- **VERIFICATION.md** - Verification checklist
- **PHASE2_SUMMARY.md** - Core functionality details
- **PHASE3_SUMMARY.md** - AI prompts and JSON outputs
- **PHASE4_SUMMARY.md** - Simulation and modular architecture
- **modules/\*\*/\*.md** - Individual module documentation

## Support

For detailed documentation on any module, see the corresponding `.md` file:
- AI: `modules/ai/*.md`
- Analytics: `modules/analytics/*.md`
- Baskets: `modules/baskets/base.md`
- Strategies: `modules/strategies/base.md`
- Simulation: `modules/simulation/engine.md`
- CLI: `modules/cli/commands.md`
- Utils: `utils/*.md`

## Next Steps

1. Read `README.md` for full feature list
2. Review `PROJECT_STRUCTURE.md` for architecture
3. Check `PHASE4_SUMMARY.md` for simulation details
4. Explore module documentation for API details
5. Start building your trading strategies!
