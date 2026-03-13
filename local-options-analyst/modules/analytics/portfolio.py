from pathlib import Path
from utils.file_io import read_json, write_json
from datetime import datetime

class Portfolio:
    def __init__(self):
        self.data_path = Path(__file__).parent.parent.parent / 'data' / 'portfolio.json'
        self.data = read_json(self.data_path)
    
    def add_position(self, basket, symbol, quantity, entry_price, position_type):
        if basket not in self.data["baskets"]:
            self.data["baskets"][basket] = []
        
        position = {
            "symbol": symbol,
            "quantity": quantity,
            "entry_price": entry_price,
            "type": position_type,
            "entry_date": datetime.now().isoformat()
        }
        self.data["baskets"][basket].append(position)
        self.data["last_updated"] = datetime.now().isoformat()
        self.save()
    
    def get_positions(self, basket=None):
        if basket:
            return self.data["baskets"].get(basket, [])
        return self.data["baskets"]
    
    def get_all_positions_flat(self):
        positions = []
        for basket, pos_list in self.data["baskets"].items():
            for pos in pos_list:
                positions.append({**pos, "basket": basket})
        return positions
    
    def calculate_valuation(self, current_prices):
        total_value = self.data["cash"]
        for basket, positions in self.data["baskets"].items():
            for pos in positions:
                current = current_prices.get(pos["symbol"], pos["entry_price"])
                value = current * pos["quantity"]
                total_value += value
        return total_value
    
    def calculate_pnl(self, current_prices, basket=None):
        total_pnl = 0
        baskets_to_calc = [basket] if basket else self.data["baskets"].keys()
        
        for b in baskets_to_calc:
            positions = self.data["baskets"].get(b, [])
            for pos in positions:
                current = current_prices.get(pos["symbol"], pos["entry_price"])
                multiplier = 1 if pos["type"] == "long" else -1
                pnl = (current - pos["entry_price"]) * pos["quantity"] * multiplier
                total_pnl += pnl
        return total_pnl
    
    def calculate_allocation(self, current_prices):
        total_value = self.calculate_valuation(current_prices)
        allocations = {}
        
        for basket, positions in self.data["baskets"].items():
            basket_value = 0
            for pos in positions:
                current = current_prices.get(pos["symbol"], pos["entry_price"])
                basket_value += current * pos["quantity"]
            allocations[basket] = (basket_value / total_value * 100) if total_value > 0 else 0
        
        allocations["cash"] = (self.data["cash"] / total_value * 100) if total_value > 0 else 0
        return allocations
    
    def save(self):
        write_json(self.data_path, self.data)
