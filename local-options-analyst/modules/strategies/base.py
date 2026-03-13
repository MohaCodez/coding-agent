from abc import ABC, abstractmethod
import json

class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, name, params=None):
        self.name = name
        self.params = params or {}
    
    @abstractmethod
    def generate_signals(self, market_data, portfolio_state):
        """Generate trading signals based on market data and portfolio."""
        pass
    
    @abstractmethod
    def get_risk_parameters(self):
        """Return risk parameters for this strategy."""
        pass


class CreditSpreadStrategy(BaseStrategy):
    """Credit spread strategy for income generation."""
    
    def generate_signals(self, market_data, portfolio_state):
        return {
            "strategy": "credit_spread",
            "signals": [],
            "note": "Implement credit spread logic"
        }
    
    def get_risk_parameters(self):
        return {
            "max_loss_per_trade": self.params.get("max_loss", 5000),
            "target_premium": self.params.get("target_premium", 2000),
            "probability_threshold": self.params.get("prob_threshold", 0.7)
        }


class IronCondorStrategy(BaseStrategy):
    """Iron condor strategy for range-bound markets."""
    
    def generate_signals(self, market_data, portfolio_state):
        return {
            "strategy": "iron_condor",
            "signals": [],
            "note": "Implement iron condor logic"
        }
    
    def get_risk_parameters(self):
        return {
            "max_loss_per_trade": self.params.get("max_loss", 8000),
            "target_premium": self.params.get("target_premium", 3000),
            "range_width": self.params.get("range_width", 500)
        }


class ProtectivePutStrategy(BaseStrategy):
    """Protective put hedging strategy."""
    
    def generate_signals(self, market_data, portfolio_state):
        return {
            "strategy": "protective_put",
            "signals": [],
            "note": "Implement protective put logic"
        }
    
    def get_risk_parameters(self):
        return {
            "hedge_ratio": self.params.get("hedge_ratio", 0.5),
            "max_cost": self.params.get("max_cost", 3000),
            "protection_level": self.params.get("protection_level", 0.95)
        }


class StrategyFactory:
    """Factory for creating strategy instances."""
    
    STRATEGY_TYPES = {
        "credit_spread": CreditSpreadStrategy,
        "iron_condor": IronCondorStrategy,
        "protective_put": ProtectivePutStrategy
    }
    
    @classmethod
    def create_strategy(cls, strategy_type, name, params=None):
        strategy_class = cls.STRATEGY_TYPES.get(strategy_type.lower())
        if not strategy_class:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        return strategy_class(name, params)
    
    @classmethod
    def register_strategy_type(cls, type_name, strategy_class):
        """Register new strategy type for extensibility."""
        cls.STRATEGY_TYPES[type_name.lower()] = strategy_class
