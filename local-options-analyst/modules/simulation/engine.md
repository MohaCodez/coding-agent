# engine.py

## Purpose
Manages persistent daily simulation with state tracking, market updates, PnL calculation, and AI-driven suggestions.

## Inputs
- `data_dir`: Path to data directory containing portfolio, trades, and simulation files

## Outputs
- Daily simulation logs with PnL, Greeks, AI suggestions
- Updated simulation.json with persistent state
- Market snapshots in daily_snapshots/
- Updated pnl_history.json

## Class: SimulationEngine

### Methods

#### `__init__(data_dir)`
Initialize simulation engine with data directory path.

#### `start_simulation(start_date=None)`
Start a new simulation.

**Inputs:**
- `start_date`: Optional ISO format date string

**Outputs:**
```python
{"status": "started", "date": "2026-03-08T15:30:00"}
```

#### `run_day()`
Execute one day of simulation.

**Outputs:**
```python
{
  "day": 1,
  "date": "2026-03-09T15:30:00",
  "valuation": 125000.0,
  "total_pnl": 5000.0,
  "basket_pnl": {"income": 3000.0, "hedge": -500.0},
  "greeks": {"delta": 25.5, "gamma": 0.05, ...},
  "ai_suggestions": "Consider closing...",
  "snapshot_file": "/path/to/snapshot.json",
  "trades_executed": [],
  "hedging_actions": []
}
```

#### `execute_suggested_trade(basket, symbol, quantity, price, position_type)`
Execute a trade and log it in current day.

**Inputs:**
- `basket`: Basket name
- `symbol`: Option symbol
- `quantity`: Number of contracts
- `price`: Execution price
- `position_type`: "long" or "short"

**Outputs:**
```python
{"status": "executed", "basket": "income", "symbol": "NIFTY24MAR21000CE"}
```

#### `log_hedging_action(action_description)`
Log hedging action in current day.

**Inputs:**
- `action_description`: Description of hedging action

#### `get_cumulative_income()`
Calculate cumulative income across all days.

**Outputs:**
```python
{
  "total": 25000.0,
  "by_basket": {
    "income": 18000.0,
    "hedge": -2000.0,
    "speculation": 9000.0
  }
}
```

#### `get_simulation_summary()`
Get complete simulation summary.

**Outputs:**
```python
{
  "state": {
    "current_day": 5,
    "start_date": "2026-03-08T15:30:00",
    "last_run": "2026-03-13T15:30:00",
    "is_active": true
  },
  "cumulative_income": {...},
  "total_days": 5,
  "recent_logs": [...]
}
```

#### `stop_simulation()`
Stop simulation.

**Outputs:**
```python
{"status": "stopped", "total_days": 5}
```

## Usage Examples

```python
from modules.simulation.engine import SimulationEngine
from pathlib import Path

# Initialize
data_dir = Path("data")
sim = SimulationEngine(data_dir)

# Start simulation
result = sim.start_simulation()
print(f"Started: {result['date']}")

# Run Day 1
day_log = sim.run_day()
print(f"Day {day_log['day']}: PnL ₹{day_log['total_pnl']:,.2f}")
print(f"AI Suggestions: {day_log['ai_suggestions']}")

# Execute suggested trade
sim.execute_suggested_trade("income", "NIFTY24MAR21000CE", 50, 150.5, "long")

# Log hedging
sim.log_hedging_action("Added protective put at 20500 strike")

# Run Day 2
day_log = sim.run_day()

# Get summary
summary = sim.get_simulation_summary()
print(f"Total Days: {summary['total_days']}")
print(f"Cumulative Income: ₹{summary['cumulative_income']['total']:,.2f}")

# Stop
sim.stop_simulation()
```

## Daily Iteration Process

1. **Update Market Prices**: Fetch or generate current prices
2. **Calculate Metrics**: Valuation, PnL per basket, Greeks
3. **Generate AI Suggestions**: Based on performance and risk
4. **Save Snapshot**: Market data and portfolio state
5. **Update PnL History**: Daily and cumulative records
6. **Log Everything**: Complete audit trail in simulation.json

## Data Logged Per Day

- Day number and date
- Portfolio valuation
- Total PnL and basket-level breakdown
- Portfolio Greeks (delta, gamma, theta, vega)
- AI suggestions for next actions
- Trades executed during the day
- Hedging actions taken
- Snapshot file location

## Use Cases

- **Multi-day backtesting**: Test strategies over time
- **Performance tracking**: Monitor cumulative income
- **AI-driven trading**: Follow AI suggestions automatically
- **Risk management**: Track Greeks evolution over time
- **Strategy validation**: Verify income generation strategies
- **Audit trail**: Complete history of all actions

## Integration with CLI

```bash
# Start simulation
python main.py sim_start

# Run days
python main.py sim_run_day

# Execute trades
python main.py sim_execute_trade income NIFTY24MAR21000CE 50 150.5 long

# View summary
python main.py sim_summary

# Stop
python main.py sim_stop
```
