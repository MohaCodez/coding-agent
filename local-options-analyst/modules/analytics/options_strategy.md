# options_strategy.py

## Purpose
AI-powered options strategy suggestions based on market view, underlying, and volatility using Qwen 3B.

## Inputs
- `market_view`: "bullish", "bearish", or "neutral"
- `underlying`: "NIFTY", "BANKNIFTY", or stock symbol
- `current_price`: Current spot price
- `volatility`: "low", "medium", or "high"

## Outputs
- 3 suitable options strategies with:
  - Strategy name and structure
  - Strike prices and expiry
  - Max profit/loss
  - Breakeven points
  - Risk-reward ratio

## Usage Examples

```python
from modules.analytics.options_strategy import OptionsStrategyAnalyzer

analyzer = OptionsStrategyAnalyzer()

# Bullish view on Nifty
result = analyzer.suggest_strategy(
    market_view="bullish",
    underlying="NIFTY",
    current_price=21500,
    volatility="medium"
)
print(result)

# Expected output:
# 1. Bull Call Spread
#    - Buy 21500 CE, Sell 21700 CE
#    - Max Profit: ₹5,000, Max Loss: ₹2,500
#    - Breakeven: 21550
#    - Risk-Reward: 1:2
```

## Strategy Categories
- **Bullish**: Bull Call Spread, Long Call, Call Ratio Spread
- **Bearish**: Bear Put Spread, Long Put, Put Ratio Spread
- **Neutral**: Iron Condor, Butterfly, Straddle/Strangle

## Use Cases
- Pre-trade strategy planning
- Risk-defined position building
- Volatility-based strategy selection
- Capital-efficient trade structuring
