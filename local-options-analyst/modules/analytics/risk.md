# risk.py

## Purpose
Calculate portfolio risk metrics including Greeks, Value at Risk (VaR), and margin requirements per NSE rules.

## Inputs
- `positions`: List of portfolio positions
- `confidence`: VaR confidence level (default: 0.95)

## Outputs
- **Greeks**: Delta, Gamma, Theta, Vega (aggregate portfolio level)
- **VaR**: Value at Risk at specified confidence level
- **Margin**: Required margin per NSE SPAN rules

## Usage Examples

```python
from modules.analytics.risk import RiskAnalyzer

analyzer = RiskAnalyzer()

positions = [
    {"symbol": "NIFTY24MAR21000CE", "quantity": 50, "type": "long"},
    {"symbol": "NIFTY24MAR21200CE", "quantity": -50, "type": "short"}
]

# Calculate Greeks
greeks = analyzer.calculate_portfolio_greeks(positions)
print(f"Portfolio Delta: {greeks['delta']}")
print(f"Portfolio Gamma: {greeks['gamma']}")

# Calculate VaR
var = analyzer.calculate_var(positions, confidence=0.95)
print(f"95% VaR: ₹{var['var']}")

# Margin requirement
margin = analyzer.margin_requirement(positions)
print(f"Required Margin: ₹{margin['margin']}")
```

## Risk Metrics Explained

### Greeks
- **Delta**: Directional exposure (positive = bullish, negative = bearish)
- **Gamma**: Rate of delta change (convexity risk)
- **Theta**: Time decay (daily P&L from time passage)
- **Vega**: Volatility sensitivity (IV change impact)

### VaR
- Maximum expected loss at given confidence level
- Example: 95% VaR of ₹10,000 = 95% chance loss won't exceed ₹10,000

### Margin
- NSE SPAN margin calculation
- Includes exposure margin and additional margins

## Implementation Notes
Current implementation returns placeholders. Integrate:
- Black-Scholes model for Greeks
- Historical simulation for VaR
- NSE SPAN margin calculator
