# base.py (Strategies)

## Purpose
Provides modular, extensible strategy system for generating trading signals and managing risk parameters.

## Architecture

### Abstract Base Class: BaseStrategy

All strategy types inherit from `BaseStrategy` and must implement:
- `generate_signals()` - Generate trading signals based on market data
- `get_risk_parameters()` - Return risk parameters for the strategy

### Built-in Strategy Types

1. **CreditSpreadStrategy** - Credit spreads for income generation
2. **IronCondorStrategy** - Iron condors for range-bound markets
3. **ProtectivePutStrategy** - Protective puts for hedging

### StrategyFactory

Factory pattern for creating strategy instances with type registration.

## Usage Examples

### Using Built-in Strategies

```python
from modules.strategies.base import StrategyFactory

# Create credit spread strategy
params = {
    "max_loss": 5000,
    "target_premium": 2000,
    "prob_threshold": 0.7
}
credit_spread = StrategyFactory.create_strategy("credit_spread", "my_spread", params)

# Generate signals
market_data = {"price": 21500, "volatility": 0.15}
portfolio_state = {"positions": [...]}
signals = credit_spread.generate_signals(market_data, portfolio_state)

# Get risk parameters
risk_params = credit_spread.get_risk_parameters()
print(f"Max Loss: ₹{risk_params['max_loss']}")
```

### Creating Custom Strategy

```python
from modules.strategies.base import BaseStrategy, StrategyFactory

class ButterflyStrategy(BaseStrategy):
    """Butterfly spread strategy for neutral outlook."""
    
    def generate_signals(self, market_data, portfolio_state):
        current_price = market_data.get("price", 0)
        
        # Generate butterfly structure
        signals = [
            {"action": "buy", "strike": current_price - 100, "quantity": 1, "type": "CE"},
            {"action": "sell", "strike": current_price, "quantity": 2, "type": "CE"},
            {"action": "buy", "strike": current_price + 100, "quantity": 1, "type": "CE"}
        ]
        
        return {
            "strategy": "butterfly",
            "signals": signals,
            "expected_premium": 1500,
            "max_profit": 8500,
            "max_loss": 1500
        }
    
    def get_risk_parameters(self):
        return {
            "max_loss": self.params.get("max_loss", 3000),
            "target_premium": self.params.get("target_premium", 1500),
            "wing_width": self.params.get("wing_width", 100)
        }

# Register
StrategyFactory.register_strategy_type("butterfly", ButterflyStrategy)

# Use
butterfly = StrategyFactory.create_strategy("butterfly", "neutral_butterfly", 
                                            params={"wing_width": 150})
signals = butterfly.generate_signals({"price": 21500}, {})
```

### Advanced Custom Strategy

```python
class AdaptiveIronCondorStrategy(BaseStrategy):
    """Iron condor that adapts to volatility."""
    
    def generate_signals(self, market_data, portfolio_state):
        price = market_data.get("price", 0)
        volatility = market_data.get("volatility", 0.15)
        
        # Adjust range based on volatility
        if volatility > 0.20:
            range_width = 600  # Wider range for high vol
        elif volatility < 0.10:
            range_width = 300  # Narrower range for low vol
        else:
            range_width = 450  # Standard range
        
        signals = [
            # Call spread
            {"action": "sell", "strike": price + range_width, "quantity": 1, "type": "CE"},
            {"action": "buy", "strike": price + range_width + 100, "quantity": 1, "type": "CE"},
            # Put spread
            {"action": "sell", "strike": price - range_width, "quantity": 1, "type": "PE"},
            {"action": "buy", "strike": price - range_width - 100, "quantity": 1, "type": "PE"}
        ]
        
        return {
            "strategy": "adaptive_iron_condor",
            "signals": signals,
            "range_width": range_width,
            "volatility_regime": "high" if volatility > 0.20 else "low" if volatility < 0.10 else "medium"
        }
    
    def get_risk_parameters(self):
        return {
            "max_loss_per_trade": 8000,
            "target_premium": 3000,
            "volatility_threshold": 0.15
        }

# Register and use
StrategyFactory.register_strategy_type("adaptive_iron_condor", AdaptiveIronCondorStrategy)
strategy = StrategyFactory.create_strategy("adaptive_iron_condor", "adaptive_ic")
```

## Class Reference

### BaseStrategy

**Abstract Methods:**
- `generate_signals(market_data, portfolio_state)` → dict
- `get_risk_parameters()` → dict

**Concrete Methods:**
- `__init__(name, params=None)` - Initialize strategy

**Inputs for generate_signals:**
- `market_data`: Dict with price, volatility, etc.
- `portfolio_state`: Dict with current positions

**Output format:**
```python
{
  "strategy": "strategy_name",
  "signals": [
    {"action": "buy/sell", "strike": 21000, "quantity": 50, "type": "CE/PE"}
  ],
  "expected_premium": 2000,
  "max_profit": 5000,
  "max_loss": 2000
}
```

### CreditSpreadStrategy

**Purpose**: Generate income through credit spreads

**Risk Parameters**:
- `max_loss_per_trade`: Maximum loss per spread
- `target_premium`: Target premium to collect
- `probability_threshold`: Minimum probability of profit

### IronCondorStrategy

**Purpose**: Profit from range-bound markets

**Risk Parameters**:
- `max_loss_per_trade`: Maximum loss
- `target_premium`: Target premium
- `range_width`: Width of profit range

### ProtectivePutStrategy

**Purpose**: Hedge portfolio with protective puts

**Risk Parameters**:
- `hedge_ratio`: Percentage of portfolio to hedge
- `max_cost`: Maximum cost of hedge
- `protection_level`: Strike selection (e.g., 95% of current price)

### StrategyFactory

**Methods:**
- `create_strategy(strategy_type, name, params=None)` → BaseStrategy
- `register_strategy_type(type_name, strategy_class)` - Register new type

## Configuration

Strategies accept parameter dictionaries:

```python
params = {
    "max_loss": 5000,
    "target_premium": 2000,
    "prob_threshold": 0.7,
    # Custom parameters
}

strategy = StrategyFactory.create_strategy("credit_spread", "my_strategy", params)
```

## Integration with Portfolio

```python
from modules.strategies.base import StrategyFactory
from modules.analytics.portfolio import Portfolio

# Create strategy
strategy = StrategyFactory.create_strategy("iron_condor", "ic_strategy")

# Get portfolio state
portfolio = Portfolio()
positions = portfolio.get_all_positions_flat()

# Generate signals
market_data = {"price": 21500, "volatility": 0.15}
signals = strategy.generate_signals(market_data, {"positions": positions})

# Execute signals
for signal in signals["signals"]:
    if signal["action"] == "buy":
        portfolio.add_position("income", f"NIFTY24MAR{signal['strike']}{signal['type']}", 
                              signal["quantity"], 150.0, "long")
```

## Extensibility Benefits

1. **Separation of Logic**: Strategy logic separate from execution
2. **Easy Testing**: Test signal generation independently
3. **Risk Management**: Built-in risk parameter tracking
4. **Reusability**: Same strategy with different parameters
5. **Custom Strategies**: Add new strategies without modifying core

## Use Cases

- **Signal Generation**: Automated trade signal generation
- **Backtesting**: Test strategies on historical data
- **Risk Assessment**: Evaluate strategy risk before execution
- **Strategy Comparison**: Compare different strategies
- **Parameter Optimization**: Test different parameter sets

## Example: Complete Workflow

```python
from modules.strategies.base import StrategyFactory, BaseStrategy

# 1. Create custom strategy
class StrangleStrategy(BaseStrategy):
    def generate_signals(self, market_data, portfolio_state):
        price = market_data["price"]
        offset = self.params.get("offset", 200)
        
        return {
            "strategy": "strangle",
            "signals": [
                {"action": "buy", "strike": price + offset, "quantity": 50, "type": "CE"},
                {"action": "buy", "strike": price - offset, "quantity": 50, "type": "PE"}
            ]
        }
    
    def get_risk_parameters(self):
        return {"max_loss": 10000, "unlimited_profit": True}

# 2. Register
StrategyFactory.register_strategy_type("strangle", StrangleStrategy)

# 3. Create and use
strangle = StrategyFactory.create_strategy("strangle", "my_strangle", 
                                           params={"offset": 250})

# 4. Generate signals
market_data = {"price": 21500, "volatility": 0.18}
signals = strangle.generate_signals(market_data, {})

# 5. Check risk
risk = strangle.get_risk_parameters()
print(f"Max Loss: ₹{risk['max_loss']}")
print(f"Signals: {len(signals['signals'])}")
```

## Best Practices

1. **Validate Inputs**: Check market_data and portfolio_state in generate_signals
2. **Return Consistent Format**: Always return dict with "strategy" and "signals"
3. **Document Parameters**: Clearly document expected params in docstring
4. **Risk Limits**: Always define max_loss in risk parameters
5. **Test Thoroughly**: Test signal generation with various market conditions
