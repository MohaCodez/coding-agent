# base.py (Baskets)

## Purpose
Provides modular, extensible basket system for organizing trading positions by strategy type.

## Architecture

### Abstract Base Class: BaseBasket

All basket types inherit from `BaseBasket` and must implement:
- `validate_position()` - Validate if position fits basket strategy
- `get_target_allocation()` - Return target allocation percentage

### Built-in Basket Types

1. **IncomeBasket** - Income generation strategies (credit spreads, iron condors)
2. **HedgeBasket** - Hedging positions (protective puts, collars)
3. **SpeculationBasket** - Speculative directional trades

### BasketFactory

Factory pattern for creating basket instances with type registration.

## Usage Examples

### Using Built-in Baskets

```python
from modules.baskets.base import BasketFactory

# Create income basket
income = BasketFactory.create_basket("income", "my_income", config={"target_allocation": 0.5})

# Add position
income.add_position("NIFTY24MAR21000CE", 50, 150.5, "long")

# Get positions
positions = income.get_positions()

# Get target allocation
allocation = income.get_target_allocation()  # 0.5 (50%)
```

### Creating Custom Basket Type

```python
from modules.baskets.base import BaseBasket, BasketFactory

class ArbitrageBasket(BaseBasket):
    """Basket for arbitrage strategies."""
    
    def validate_position(self, symbol, quantity, price, position_type):
        # Custom validation logic
        # Example: Ensure paired positions for arbitrage
        return True
    
    def get_target_allocation(self):
        return self.config.get("target_allocation", 0.15)  # 15% default

# Register new basket type
BasketFactory.register_basket_type("arbitrage", ArbitrageBasket)

# Create instance
arb_basket = BasketFactory.create_basket("arbitrage", "my_arbitrage")
```

### Advanced Custom Basket

```python
class VolatilityBasket(BaseBasket):
    """Basket for volatility trading strategies."""
    
    def validate_position(self, symbol, quantity, price, position_type):
        # Only allow straddles/strangles
        if "CE" in symbol or "PE" in symbol:
            return True
        return False
    
    def get_target_allocation(self):
        return self.config.get("target_allocation", 0.2)
    
    def calculate_vega_exposure(self):
        """Custom method for volatility basket."""
        total_vega = 0
        for pos in self.positions:
            # Calculate vega per position
            vega = pos["quantity"] * 0.1  # Simplified
            total_vega += vega
        return total_vega

# Register
BasketFactory.register_basket_type("volatility", VolatilityBasket)

# Use
vol_basket = BasketFactory.create_basket("volatility", "vol_trades", 
                                         config={"target_allocation": 0.2})
vol_basket.add_position("NIFTY24MAR21000CE", 50, 150.5, "long")
vega = vol_basket.calculate_vega_exposure()
```

## Class Reference

### BaseBasket

**Abstract Methods:**
- `validate_position(symbol, quantity, price, position_type)` → bool
- `get_target_allocation()` → float

**Concrete Methods:**
- `__init__(name, config=None)` - Initialize basket
- `add_position(symbol, quantity, price, position_type)` → bool
- `get_positions()` → list

### IncomeBasket

**Purpose**: Income generation through premium collection

**Default Allocation**: 50%

**Typical Strategies**: Credit spreads, iron condors, covered calls

### HedgeBasket

**Purpose**: Portfolio protection and risk management

**Default Allocation**: 20%

**Typical Strategies**: Protective puts, collars, bear spreads

### SpeculationBasket

**Purpose**: Directional trades and speculation

**Default Allocation**: 30%

**Typical Strategies**: Long calls/puts, debit spreads, ratio spreads

### BasketFactory

**Methods:**
- `create_basket(basket_type, name, config=None)` → BaseBasket
- `register_basket_type(type_name, basket_class)` - Register new type

## Configuration

Baskets accept configuration dictionaries:

```python
config = {
    "target_allocation": 0.4,  # 40% of portfolio
    "max_positions": 10,
    "risk_limit": 50000,
    # Custom parameters
}

basket = BasketFactory.create_basket("income", "my_basket", config)
```

## Integration with Portfolio

```python
from modules.analytics.portfolio import Portfolio
from modules.baskets.base import BasketFactory

portfolio = Portfolio()

# Baskets are automatically managed in portfolio.json
# Add position to basket
portfolio.add_position("income", "NIFTY24MAR21000CE", 50, 150.5, "long")

# Get basket positions
income_positions = portfolio.get_positions("income")
```

## Extensibility Benefits

1. **Type Safety**: Abstract base class enforces interface
2. **Easy Addition**: Register new types without modifying existing code
3. **Validation**: Each basket validates its own positions
4. **Allocation Management**: Built-in target allocation tracking
5. **Custom Logic**: Add basket-specific methods and properties

## Use Cases

- **Strategy Segregation**: Separate income, hedge, speculation
- **Risk Management**: Track exposure per basket type
- **Performance Analysis**: Compare basket performance
- **Allocation Rebalancing**: Maintain target allocations
- **Custom Strategies**: Add new basket types for specific strategies

## Example: Complete Workflow

```python
from modules.baskets.base import BasketFactory, BaseBasket

# 1. Create custom basket
class MomentumBasket(BaseBasket):
    def validate_position(self, symbol, quantity, price, position_type):
        return position_type == "long"  # Only long positions
    
    def get_target_allocation(self):
        return 0.25

# 2. Register
BasketFactory.register_basket_type("momentum", MomentumBasket)

# 3. Create instance
momentum = BasketFactory.create_basket("momentum", "momentum_trades")

# 4. Add positions
momentum.add_position("NIFTY24MAR21500CE", 100, 120.0, "long")

# 5. Get info
print(f"Positions: {len(momentum.get_positions())}")
print(f"Target Allocation: {momentum.get_target_allocation():.0%}")
```
