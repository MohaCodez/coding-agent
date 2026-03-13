# Local Indian Options Trading Analyst

A local AI-powered options trading analyst for Indian markets using Ollama Qwen 3B with persistent simulation capabilities.

## Features

- **Basket-based portfolio management** with persistent storage
- **AI-powered analysis** using Qwen 3B with structured JSON outputs
- **Persistent simulation engine** with daily iterations and state tracking
- **Income strategy formulation** with credit spreads, iron condors, covered calls
- **Hedging recommendations** for risk management
- **Market sentiment analysis** with -1 to 1 scoring per underlying
- **Risk analytics** (Greeks, VaR, margin per basket)
- **Daily PnL tracking** with basket-level breakdown and cumulative income
- **Trade history** with complete audit trail
- **Market data snapshots** for historical analysis
- **Modular architecture** for easy extension (baskets, strategies, asset types)
- **Fully local execution** - no cloud dependencies

## Setup

1. Install Ollama: https://ollama.ai
2. Pull the model:
   ```bash
   ollama pull qwen2.5:3b
   ```
3. Install dependencies:
   ```bash
   cd local-options-analyst
   pip install -r requirements.txt
   ```

## Quick Start

### Basic Workflow
```bash
# Add positions
python main.py add_trade income NIFTY24MAR21000CE 50 150.5 long
python main.py add_trade hedge NIFTY24MAR20500PE 25 80.0 long

# Analyze portfolio
python main.py analyze

# View report
python main.py report
```

### Simulation Workflow (NEW - Phase 4)
```bash
# 1. Start simulation
python main.py sim_start

# 2. Run daily iterations
python main.py sim_run_day  # Day 1
python main.py sim_run_day  # Day 2
python main.py sim_run_day  # Day 3

# 3. Execute suggested trades
python main.py sim_execute_trade income NIFTY24MAR21200CE 50 125.0 short

# 4. Log hedging actions
python main.py sim_log_hedge "Added protective put at 20500"

# 5. View cumulative results
python main.py sim_summary

# 6. Stop simulation
python main.py sim_stop
```

## Commands Reference

### Portfolio Management
| Command | Description |
|---------|-------------|
| `add_trade` | Add trade to basket |
| `analyze` | AI analysis with metrics |
| `report` | Portfolio summary |
| `portfolio` | View portfolio (alias) |

### Strategy & Analysis
| Command | Description |
|---------|-------------|
| `formulate_income` | Generate income strategies (JSON) |
| `strategy` | Strategy suggestions |
| `sentiment` | Sentiment analysis (text/JSON) |

### Simulation (Phase 4)
| Command | Description |
|---------|-------------|
| `sim_start` | Start simulation |
| `sim_run_day` | Run one day iteration |
| `sim_execute_trade` | Execute trade in simulation |
| `sim_log_hedge` | Log hedging action |
| `sim_summary` | View cumulative results |
| `sim_stop` | Stop simulation |

### Legacy
| Command | Description |
|---------|-------------|
| `run_day` | Single day update (non-persistent) |

## Detailed Usage

### Add Trade to Basket
```bash
python main.py add_trade income NIFTY24MAR21000CE 50 150.5 long
python main.py add_trade hedge NIFTY24MAR20500PE 25 80.0 long
python main.py add_trade speculation BANKNIFTY24MAR45000CE 10 200.0 short
```

### Analyze Portfolio
```bash
python main.py analyze
# Shows: valuation, allocations, Greeks, AI insights with trade history analysis
```

### Formulate Income Strategy
```bash
python main.py formulate_income \
  --target 15000 \
  --view bullish \
  --underlying NIFTY \
  --price 21500 \
  --volatility medium \
  --risk medium

# Returns JSON with:
# - Suggested trades (credit spreads, iron condors)
# - Hedging recommendations
# - Expected income (monthly/annual)
# - Risk summary (margin, max loss, risk-reward)
```

### Sentiment Analysis
```bash
# Text format (human-readable)
python main.py sentiment "RBI maintains repo rate, dovish stance on inflation"

# Simplified JSON (specific underlying)
python main.py sentiment "FII selling continues" --json --underlying NIFTY

# Full JSON (all underlyings + trading implications)
python main.py sentiment "Market rally on positive earnings" --full
```

### Simulation Commands

#### Start Simulation
```bash
python main.py sim_start
python main.py sim_start --date 2026-03-01T00:00:00
```

#### Run Daily Iteration
```bash
python main.py sim_run_day
```
**Output**: Day number, valuation, PnL, Greeks, AI suggestions, snapshot location

#### Execute Suggested Trade
```bash
python main.py sim_execute_trade income NIFTY24MAR21000CE 50 150.5 long
```

#### Log Hedging Action
```bash
python main.py sim_log_hedge "Added protective put at 20500 strike"
```

#### View Summary
```bash
python main.py sim_summary
```
**Output**: Status, total days, cumulative income (total + per basket), recent days

#### Stop Simulation
```bash
python main.py sim_stop
```

## Architecture

```
CLI (commands.py)
  ↓
Simulation Engine (engine.py) ← Phase 4
  ↓
Analytics Layer (portfolio.py, options_strategy.py, risk.py)
  ↓
AI Layer (qwen_interface.py, sentiment.py) → Enhanced Prompts (Phase 3)
  ↓
Modular Components (baskets/, strategies/) ← Phase 4
  ↓
Data Layer (JSON files) + Utils (file_io.py, market_fetcher.py)
```

## Modular Design (Phase 4)

### Add New Basket Type
```python
from modules.baskets.base import BaseBasket, BasketFactory

class ArbitrageBasket(BaseBasket):
    def validate_position(self, symbol, quantity, price, position_type):
        return True  # Custom validation
    
    def get_target_allocation(self):
        return 0.15  # 15% allocation

BasketFactory.register_basket_type("arbitrage", ArbitrageBasket)
```

### Add New Strategy
```python
from modules.strategies.base import BaseStrategy, StrategyFactory

class ButterflyStrategy(BaseStrategy):
    def generate_signals(self, market_data, portfolio_state):
        return {"strategy": "butterfly", "signals": [...]}
    
    def get_risk_parameters(self):
        return {"max_loss": 3000, "target_premium": 1500}

StrategyFactory.register_strategy_type("butterfly", ButterflyStrategy)
```

## Data Structure

### simulation.json (NEW)
```json
{
  "simulation_state": {
    "current_day": 5,
    "start_date": "2026-03-08T15:30:00",
    "last_run": "2026-03-13T15:30:00",
    "is_active": true
  },
  "daily_logs": [
    {
      "day": 1,
      "date": "2026-03-09T15:30:00",
      "valuation": 125000.0,
      "total_pnl": 5000.0,
      "basket_pnl": {...},
      "greeks": {...},
      "ai_suggestions": "...",
      "trades_executed": [...],
      "hedging_actions": [...]
    }
  ]
}
```

### portfolio.json
```json
{
  "cash": 100000.0,
  "baskets": {
    "income": [...positions...],
    "hedge": [...positions...],
    "speculation": [...positions...]
  },
  "last_updated": "2026-03-08T15:30:00"
}
```

## Complete Example

```bash
# Setup
python main.py add_trade income NIFTY24MAR21000CE 50 150.5 long
python main.py add_trade income NIFTY24MAR21200CE 50 120.0 short
python main.py add_trade hedge NIFTY24MAR20500PE 25 80.0 long

# Start simulation
python main.py sim_start

# Run 5 days
for i in {1..5}; do python main.py sim_run_day; done

# View results
python main.py sim_summary

# Analyze sentiment
python main.py sentiment "RBI dovish stance" --full

# Formulate new income strategy
python main.py formulate_income --target 20000 --view neutral --underlying NIFTY --price 21500

# Stop
python main.py sim_stop
```

## Documentation

- `PHASE2_SUMMARY.md` - Core functionality details
- `PHASE3_SUMMARY.md` - AI prompts and JSON outputs
- `PHASE4_SUMMARY.md` - Simulation engine and modular architecture
- Individual `.md` files in module directories for API documentation

## Note

Market data fetching uses mock prices for testing. Integrate with NSE API or data provider for live data.
