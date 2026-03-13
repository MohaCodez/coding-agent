# portfolio.py

## Purpose
Manages trading portfolio with persistent storage, position tracking, and PnL calculation.

## Inputs
- `symbol`: Option symbol (e.g., "NIFTY24MAR21000CE")
- `quantity`: Number of contracts
- `entry_price`: Entry price in ₹
- `position_type`: "long" or "short"
- `current_prices`: Dict of current market prices for PnL calculation

## Outputs
- Position confirmation
- List of all positions
- Total PnL calculation
- Updated portfolio.json file

## Usage Examples

```python
from modules.analytics.portfolio import Portfolio

portfolio = Portfolio()

# Add position
portfolio.add_position("NIFTY24MAR21000CE", 50, 150.5, "long")
portfolio.add_position("BANKNIFTY24MAR45000PE", 25, 200.0, "short")

# Get all positions
positions = portfolio.get_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['quantity']} @ ₹{pos['entry_price']}")

# Calculate PnL
current_prices = {
    "NIFTY24MAR21000CE": 175.0,
    "BANKNIFTY24MAR45000PE": 180.0
}
pnl = portfolio.calculate_pnl(current_prices)
print(f"Total PnL: ₹{pnl:.2f}")
```

## Data Structure
```json
{
  "positions": [
    {
      "symbol": "NIFTY24MAR21000CE",
      "quantity": 50,
      "entry_price": 150.5,
      "type": "long",
      "entry_date": "2026-03-08T15:30:00"
    }
  ],
  "cash": 100000.0,
  "last_updated": "2026-03-08T15:30:00"
}
```
