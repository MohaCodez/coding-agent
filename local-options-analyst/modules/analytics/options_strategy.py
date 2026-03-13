from modules.ai.qwen_interface import QwenInterface
from utils.file_io import read_prompt
import json

class OptionsStrategyAnalyzer:
    def __init__(self):
        self.qwen = QwenInterface()
    
    def suggest_strategy(self, market_view, underlying, current_price, volatility):
        prompt_template = read_prompt('strategy_suggestion_prompt')
        prompt = prompt_template.format(
            market_view=market_view,
            underlying=underlying,
            current_price=current_price,
            volatility=volatility
        )
        return self.qwen.generate(prompt)
    
    def formulate_income_strategy(self, target_income, portfolio_summary, market_view, 
                                   underlying, current_price, volatility="medium", 
                                   risk_tolerance="medium"):
        """Generate income strategies with structured JSON output."""
        prompt_template = read_prompt('options_strategy_prompt')
        prompt = prompt_template.format(
            target_income=target_income,
            portfolio_summary=json.dumps(portfolio_summary, indent=2),
            market_view=market_view,
            underlying=underlying,
            current_price=current_price,
            volatility=volatility,
            risk_tolerance=risk_tolerance
        )
        
        response = self.qwen.generate(prompt, temperature=0.5)
        return self._parse_strategy_json(response)
    
    def suggest_income_strategies(self, portfolio_data, risk_tolerance="medium"):
        """Generate income-focused options strategies."""
        prompt = f"""Based on this portfolio:
{portfolio_data}

Risk tolerance: {risk_tolerance}

Suggest 3 income-generating options strategies (credit spreads, iron condors, covered calls) with:
1. Strategy structure and strikes
2. Expected monthly income
3. Risk profile
4. Margin requirement
"""
        return self.qwen.generate(prompt)
    
    def suggest_hedging(self, positions, market_scenario):
        """Suggest hedging strategies for existing positions."""
        prompt = f"""Current positions:
{positions}

Market scenario: {market_scenario}

Suggest hedging strategies to protect downside with:
1. Hedge structure (puts, collars, spreads)
2. Cost of hedge
3. Protection level
4. Impact on overall portfolio
"""
        return self.qwen.generate(prompt)
    
    def _parse_strategy_json(self, response):
        """Extract and parse JSON from AI response."""
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            pass
        
        # Return fallback structure
        return {
            "suggested_trades": [],
            "hedging_recommendations": [],
            "expected_income": {"monthly": 0, "annualized": 0, "return_on_capital": 0},
            "risk_summary": {"total_margin": 0, "max_loss": 0, "risk_reward_ratio": 0},
            "error": "Failed to parse JSON response"
        }
