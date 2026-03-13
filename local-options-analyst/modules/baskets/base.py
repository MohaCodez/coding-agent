from abc import ABC, abstractmethod
from pathlib import Path
from utils.file_io import read_json, write_json
import json

class BaseBasket(ABC):
    """Abstract base class for trading baskets."""
    
    def __init__(self, name, config=None):
        self.name = name
        self.config = config or {}
        self.positions = []
    
    @abstractmethod
    def validate_position(self, symbol, quantity, price, position_type):
        """Validate if position fits basket strategy."""
        pass
    
    @abstractmethod
    def get_target_allocation(self):
        """Return target allocation percentage."""
        pass
    
    def add_position(self, symbol, quantity, price, position_type):
        if self.validate_position(symbol, quantity, price, position_type):
            self.positions.append({
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "type": position_type
            })
            return True
        return False
    
    def get_positions(self):
        return self.positions


class IncomeBasket(BaseBasket):
    """Basket for income generation strategies."""
    
    def validate_position(self, symbol, quantity, price, position_type):
        # Income strategies typically involve credit spreads, iron condors
        return True  # Add specific validation logic
    
    def get_target_allocation(self):
        return self.config.get("target_allocation", 0.5)  # 50% default


class HedgeBasket(BaseBasket):
    """Basket for hedging positions."""
    
    def validate_position(self, symbol, quantity, price, position_type):
        # Hedges are typically protective puts, collars
        return True  # Add specific validation logic
    
    def get_target_allocation(self):
        return self.config.get("target_allocation", 0.2)  # 20% default


class SpeculationBasket(BaseBasket):
    """Basket for speculative trades."""
    
    def validate_position(self, symbol, quantity, price, position_type):
        # Speculation can be any directional trade
        return True  # Add specific validation logic
    
    def get_target_allocation(self):
        return self.config.get("target_allocation", 0.3)  # 30% default


class BasketFactory:
    """Factory for creating basket instances."""
    
    BASKET_TYPES = {
        "income": IncomeBasket,
        "hedge": HedgeBasket,
        "speculation": SpeculationBasket
    }
    
    @classmethod
    def create_basket(cls, basket_type, name, config=None):
        basket_class = cls.BASKET_TYPES.get(basket_type.lower())
        if not basket_class:
            raise ValueError(f"Unknown basket type: {basket_type}")
        return basket_class(name, config)
    
    @classmethod
    def register_basket_type(cls, type_name, basket_class):
        """Register new basket type for extensibility."""
        cls.BASKET_TYPES[type_name.lower()] = basket_class
