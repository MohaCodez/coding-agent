from pathlib import Path
from utils.file_io import read_json, write_json
from utils.market_fetcher import get_real_prices, save_market_snapshot
from modules.analytics.portfolio import Portfolio
from modules.analytics.risk import RiskAnalyzer
from modules.ai.qwen_interface import QwenInterface
from datetime import datetime, timedelta
import json

class SimulationEngine:
    """Manages persistent daily simulation with state tracking."""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.sim_path = self.data_dir / 'simulation.json'
        self.portfolio = Portfolio()
        self.risk_analyzer = RiskAnalyzer()
        self.qwen = QwenInterface()
        self.state = self._load_state()
    
    def _load_state(self):
        return read_json(self.sim_path)
    
    def _save_state(self):
        write_json(self.sim_path, self.state)
    
    def start_simulation(self, start_date=None):
        """Initialize simulation."""
        self.state["simulation_state"]["is_active"] = True
        self.state["simulation_state"]["start_date"] = start_date or datetime.now().isoformat()
        self.state["simulation_state"]["current_day"] = 0
        self._save_state()
        return {"status": "started", "date": self.state["simulation_state"]["start_date"]}
    
    def run_day(self):
        """Execute one day of simulation."""
        if not self.state["simulation_state"]["is_active"]:
            return {"error": "Simulation not active. Run start_simulation first."}
        
        day_num = self.state["simulation_state"]["current_day"] + 1
        sim_date = datetime.fromisoformat(self.state["simulation_state"]["start_date"]) + timedelta(days=day_num)
        
        # Get positions
        positions = self.portfolio.get_all_positions_flat()
        if not positions:
            return {"error": "No positions to simulate"}
        
        # Update market prices
        symbols = list(set([p["symbol"] for p in positions]))
        current_prices = get_real_prices(symbols)
        
        # Calculate metrics
        valuation = self.portfolio.calculate_valuation(current_prices)
        baskets = self.portfolio.get_positions()
        basket_pnl = {}
        
        for basket in baskets.keys():
            basket_pnl[basket] = self.portfolio.calculate_pnl(current_prices, basket)
        
        total_pnl = sum(basket_pnl.values())
        greeks = self.risk_analyzer.calculate_portfolio_greeks(positions)
        
        # AI suggestions
        ai_prompt = f"""Day {day_num} Analysis:
Portfolio PnL: ₹{total_pnl:,.2f}
Basket PnL: {json.dumps(basket_pnl, indent=2)}
Greeks: {json.dumps(greeks, indent=2)}

Suggest:
1. Positions to adjust/close
2. New opportunities
3. Risk management actions
"""
        ai_suggestions = self.qwen.generate(ai_prompt, temperature=0.7)
        
        # Save snapshot
        snapshot_data = {
            "date": sim_date.isoformat(),
            "day": day_num,
            "prices": current_prices,
            "valuation": valuation,
            "total_pnl": total_pnl,
            "basket_pnl": basket_pnl,
            "greeks": greeks
        }
        snapshot_file = save_market_snapshot(f"day_{day_num}", snapshot_data, self.data_dir)
        
        # Update PnL history
        pnl_history_path = self.data_dir / 'pnl_history.json'
        history = read_json(pnl_history_path)
        
        history["daily_pnl"].append({
            "date": sim_date.isoformat(),
            "day": day_num,
            "total_pnl": total_pnl,
            "basket_pnl": basket_pnl
        })
        
        for basket, pnl in basket_pnl.items():
            if basket not in history["basket_pnl"]:
                history["basket_pnl"][basket] = []
            history["basket_pnl"][basket].append({
                "date": sim_date.isoformat(),
                "day": day_num,
                "pnl": pnl
            })
        
        write_json(pnl_history_path, history)
        
        # Log day results
        day_log = {
            "day": day_num,
            "date": sim_date.isoformat(),
            "valuation": valuation,
            "total_pnl": total_pnl,
            "basket_pnl": basket_pnl,
            "greeks": greeks,
            "ai_suggestions": ai_suggestions,
            "snapshot_file": str(snapshot_file),
            "trades_executed": [],
            "hedging_actions": []
        }
        
        self.state["daily_logs"].append(day_log)
        self.state["simulation_state"]["current_day"] = day_num
        self.state["simulation_state"]["last_run"] = datetime.now().isoformat()
        self._save_state()
        
        return day_log
    
    def execute_suggested_trade(self, basket, symbol, quantity, price, position_type):
        """Execute a trade and log it in current day."""
        self.portfolio.add_position(basket, symbol, quantity, price, position_type)
        
        # Log in current day
        if self.state["daily_logs"]:
            current_day_log = self.state["daily_logs"][-1]
            current_day_log["trades_executed"].append({
                "basket": basket,
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "type": position_type,
                "timestamp": datetime.now().isoformat()
            })
            self._save_state()
        
        return {"status": "executed", "basket": basket, "symbol": symbol}
    
    def log_hedging_action(self, action_description):
        """Log hedging action in current day."""
        if self.state["daily_logs"]:
            current_day_log = self.state["daily_logs"][-1]
            current_day_log["hedging_actions"].append({
                "description": action_description,
                "timestamp": datetime.now().isoformat()
            })
            self._save_state()
    
    def get_cumulative_income(self):
        """Calculate cumulative income across all days."""
        total = 0
        basket_totals = {}
        
        for log in self.state["daily_logs"]:
            total += log["total_pnl"]
            for basket, pnl in log["basket_pnl"].items():
                basket_totals[basket] = basket_totals.get(basket, 0) + pnl
        
        return {"total": total, "by_basket": basket_totals}
    
    def get_simulation_summary(self):
        """Get complete simulation summary."""
        return {
            "state": self.state["simulation_state"],
            "cumulative_income": self.get_cumulative_income(),
            "total_days": len(self.state["daily_logs"]),
            "recent_logs": self.state["daily_logs"][-5:] if self.state["daily_logs"] else []
        }
    
    def stop_simulation(self):
        """Stop simulation."""
        self.state["simulation_state"]["is_active"] = False
        self._save_state()
        return {"status": "stopped", "total_days": self.state["simulation_state"]["current_day"]}
