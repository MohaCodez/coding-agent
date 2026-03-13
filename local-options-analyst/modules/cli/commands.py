import argparse
from modules.analytics.portfolio import Portfolio
from modules.analytics.options_strategy import OptionsStrategyAnalyzer
from modules.ai.sentiment import SentimentAnalyzer
from modules.analytics.risk import RiskAnalyzer
from modules.simulation.engine import SimulationEngine
from pathlib import Path
from utils.file_io import read_json, write_json, read_prompt, append_trade
from modules.ai.qwen_interface import QwenInterface
from utils.market_fetcher import get_real_prices, save_market_snapshot
from datetime import datetime
import json

class CLI:
    def __init__(self):
        self.portfolio = Portfolio()
        self.strategy_analyzer = OptionsStrategyAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.risk_analyzer = RiskAnalyzer()
        self.qwen = QwenInterface()
        self.data_dir = Path(__file__).parent.parent.parent / 'data'
        self.simulation = SimulationEngine(self.data_dir)
    
    def add_trade(self, args):
        """Add trade to basket and record in trades.json."""
        self.portfolio.add_position(args.basket, args.symbol, args.quantity, args.price, args.type)
        
        # Record trade
        trade = {
            "date": datetime.now().isoformat(),
            "action": "buy" if args.type == "long" else "sell",
            "basket": args.basket,
            "symbol": args.symbol,
            "quantity": args.quantity,
            "price": args.price
        }
        append_trade(trade, self.data_dir / 'trades.json')
        
        print(f"✓ Added {args.type} trade to basket '{args.basket}': {args.symbol} x{args.quantity} @ ₹{args.price}")
    
    def analyze(self, args):
        """Run AI analysis and compute metrics."""
        positions = self.portfolio.get_all_positions_flat()
        
        if not positions:
            print("No positions to analyze")
            return
        
        # Get mock prices
        symbols = list(set([p["symbol"] for p in positions]))
        current_prices = get_real_prices(symbols)
        
        # Calculate metrics
        valuation = self.portfolio.calculate_valuation(current_prices)
        allocations = self.portfolio.calculate_allocation(current_prices)
        greeks = self.risk_analyzer.calculate_portfolio_greeks(positions)
        
        print("\n=== Portfolio Analysis ===")
        print(f"Total Valuation: ₹{valuation:,.2f}")
        print(f"\nAllocations:")
        for basket, pct in allocations.items():
            print(f"  {basket}: {pct:.2f}%")
        
        print(f"\nGreeks:")
        for greek, value in greeks.items():
            print(f"  {greek.capitalize()}: {value}")
        
        # Load trade history
        trades_data = read_json(self.data_dir / 'trades.json')
        
        # AI Analysis with enhanced prompt
        prompt_template = read_prompt('portfolio_prompt')
        portfolio_summary = {
            "positions": positions,
            "valuation": valuation,
            "allocations": allocations,
            "greeks": greeks
        }
        prompt = prompt_template.format(
            portfolio_data=json.dumps(portfolio_summary, indent=2),
            trade_history=json.dumps(trades_data["trades"][-10:], indent=2)  # Last 10 trades
        )
        analysis = self.qwen.generate(prompt)
        
        print("\n=== AI Insights ===")
        print(analysis)
    
    def run_day(self, args):
        """Simulate daily iteration: update PnL, suggest trades."""
        positions = self.portfolio.get_all_positions_flat()
        
        if not positions:
            print("No positions. Add trades first.")
            return
        
        # Get mock prices
        symbols = list(set([p["symbol"] for p in positions]))
        current_prices = get_real_prices(symbols)
        
        # Calculate PnL per basket
        baskets = self.portfolio.get_positions()
        pnl_data = {}
        
        print("\n=== Daily PnL Update ===")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        for basket in baskets.keys():
            pnl = self.portfolio.calculate_pnl(current_prices, basket)
            pnl_data[basket] = pnl
            print(f"  {basket}: ₹{pnl:,.2f}")
        
        total_pnl = sum(pnl_data.values())
        print(f"\nTotal PnL: ₹{total_pnl:,.2f}")
        
        # Save to history
        history_path = self.data_dir / 'pnl_history.json'
        history = read_json(history_path)
        
        history["daily_pnl"].append({
            "date": datetime.now().isoformat(),
            "total_pnl": total_pnl,
            "basket_pnl": pnl_data
        })
        
        # Update basket cumulative PnL
        for basket, pnl in pnl_data.items():
            if basket not in history["basket_pnl"]:
                history["basket_pnl"][basket] = []
            history["basket_pnl"][basket].append({
                "date": datetime.now().isoformat(),
                "pnl": pnl
            })
        
        write_json(history_path, history)
        
        # Save market snapshot
        snapshot_data = {
            "date": datetime.now().isoformat(),
            "prices": current_prices
        }
        snapshot_file = save_market_snapshot("portfolio", snapshot_data, self.data_dir)
        print(f"\n✓ Saved snapshot: {snapshot_file}")
        
        # AI suggestions
        print("\n=== AI Trade Suggestions ===")
        prompt = f"""Based on today's PnL and market conditions:
Portfolio PnL: ₹{total_pnl:,.2f}
Basket PnL: {json.dumps(pnl_data, indent=2)}

Suggest:
1. Positions to adjust or close
2. New opportunities
3. Risk management actions
"""
        suggestions = self.qwen.generate(prompt)
        print(suggestions)
    
    def report(self, args):
        """Show portfolio summary and PnL report."""
        positions = self.portfolio.get_all_positions_flat()
        
        if not positions:
            print("Portfolio is empty")
            return
        
        # Get mock prices
        symbols = list(set([p["symbol"] for p in positions]))
        current_prices = get_real_prices(symbols)
        
        print("\n" + "="*60)
        print("PORTFOLIO REPORT")
        print("="*60)
        
        # Positions by basket
        baskets = self.portfolio.get_positions()
        for basket, pos_list in baskets.items():
            print(f"\n[{basket}]")
            for pos in pos_list:
                current = current_prices.get(pos["symbol"], pos["entry_price"])
                pnl = (current - pos["entry_price"]) * pos["quantity"]
                print(f"  {pos['symbol']:<25} {pos['type']:<6} Qty:{pos['quantity']:>4} Entry:₹{pos['entry_price']:>7.2f} Current:₹{current:>7.2f} PnL:₹{pnl:>8.2f}")
        
        # Summary
        valuation = self.portfolio.calculate_valuation(current_prices)
        total_pnl = self.portfolio.calculate_pnl(current_prices)
        allocations = self.portfolio.calculate_allocation(current_prices)
        
        print("\n" + "-"*60)
        print(f"Total Valuation: ₹{valuation:,.2f}")
        print(f"Total PnL: ₹{total_pnl:,.2f}")
        print(f"Cash: ₹{self.portfolio.data['cash']:,.2f}")
        
        print("\nAllocations:")
        for basket, pct in allocations.items():
            print(f"  {basket}: {pct:.2f}%")
        
        # Historical PnL
        history = read_json(self.data_dir / 'pnl_history.json')
        if history["daily_pnl"]:
            print("\nRecent PnL History:")
            for entry in history["daily_pnl"][-5:]:
                date = entry["date"][:10]
                pnl = entry["total_pnl"]
                print(f"  {date}: ₹{pnl:,.2f}")
        
        print("="*60)
    
    def view_portfolio(self, args):
        """Legacy command - redirects to report."""
        self.report(args)
    
    def suggest_strategy(self, args):
        result = self.strategy_analyzer.suggest_strategy(
            args.view, args.underlying, args.price, args.volatility
        )
        print("\n=== Strategy Suggestions ===")
        print(result)
    
    def analyze_sentiment(self, args):
        if args.json:
            result = self.sentiment_analyzer.analyze_json(args.text, args.underlying)
            print(json.dumps(result, indent=2))
        elif args.full:
            result = self.sentiment_analyzer.analyze(args.text)
            print(json.dumps(result, indent=2))
        else:
            result = self.sentiment_analyzer.analyze_text(args.text)
            print("\n=== Sentiment Analysis ===")
            print(result)
    
    def formulate_income(self, args):
        """Formulate income generation strategy with JSON output."""
        positions = self.portfolio.get_all_positions_flat()
        symbols = list(set([p["symbol"] for p in positions])) if positions else []
        current_prices = get_real_prices(symbols) if symbols else {}
        
        portfolio_summary = {
            "positions": positions,
            "valuation": self.portfolio.calculate_valuation(current_prices) if positions else 0,
            "cash": self.portfolio.data["cash"]
        }
        
        result = self.strategy_analyzer.formulate_income_strategy(
            target_income=args.target,
            portfolio_summary=portfolio_summary,
            market_view=args.view,
            underlying=args.underlying,
            current_price=args.price,
            volatility=args.volatility,
            risk_tolerance=args.risk
        )
        
        print("\n=== Income Strategy Formulation ===")
        print(json.dumps(result, indent=2))
    
    def sim_start(self, args):
        """Start simulation."""
        result = self.simulation.start_simulation(args.date)
        print(f"✓ Simulation started: {result['date']}")
    
    def sim_run_day(self, args):
        """Run one day of simulation."""
        result = self.simulation.run_day()
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        print(f"\n=== Day {result['day']} Simulation ===")
        print(f"Date: {result['date'][:10]}")
        print(f"Valuation: ₹{result['valuation']:,.2f}")
        print(f"Total PnL: ₹{result['total_pnl']:,.2f}")
        
        print("\nBasket PnL:")
        for basket, pnl in result['basket_pnl'].items():
            print(f"  {basket}: ₹{pnl:,.2f}")
        
        print("\nGreeks:")
        for greek, value in result['greeks'].items():
            print(f"  {greek}: {value}")
        
        print("\n=== AI Suggestions ===")
        print(result['ai_suggestions'])
        
        print(f"\n✓ Snapshot saved: {result['snapshot_file']}")
    
    def sim_execute_trade(self, args):
        """Execute suggested trade in simulation."""
        result = self.simulation.execute_suggested_trade(
            args.basket, args.symbol, args.quantity, args.price, args.type
        )
        print(f"✓ Trade executed in simulation: {result['symbol']} in basket '{result['basket']}'")
    
    def sim_log_hedge(self, args):
        """Log hedging action."""
        self.simulation.log_hedging_action(args.description)
        print(f"✓ Hedging action logged: {args.description}")
    
    def sim_summary(self, args):
        """Show simulation summary."""
        summary = self.simulation.get_simulation_summary()
        
        print("\n=== Simulation Summary ===")
        print(f"Status: {'Active' if summary['state']['is_active'] else 'Stopped'}")
        print(f"Total Days: {summary['total_days']}")
        print(f"Start Date: {summary['state']['start_date'][:10] if summary['state']['start_date'] else 'N/A'}")
        
        cumulative = summary['cumulative_income']
        print(f"\nCumulative Income: ₹{cumulative['total']:,.2f}")
        print("\nBy Basket:")
        for basket, total in cumulative['by_basket'].items():
            print(f"  {basket}: ₹{total:,.2f}")
        
        if summary['recent_logs']:
            print("\nRecent Days:")
            for log in summary['recent_logs']:
                print(f"  Day {log['day']}: PnL ₹{log['total_pnl']:,.2f}")
    
    def sim_stop(self, args):
        """Stop simulation."""
        result = self.simulation.stop_simulation()
        print(f"✓ Simulation stopped after {result['total_days']} days")

def run():
    parser = argparse.ArgumentParser(description="Local Indian Options Trading Analyst")
    subparsers = parser.add_subparsers(dest='command')
    
    # Add trade
    add_parser = subparsers.add_parser('add_trade', help='Add trade to basket')
    add_parser.add_argument('basket', help='Basket name')
    add_parser.add_argument('symbol', help='Symbol (e.g., NIFTY24MAR21000CE)')
    add_parser.add_argument('quantity', type=int, help='Quantity')
    add_parser.add_argument('price', type=float, help='Entry price')
    add_parser.add_argument('type', choices=['long', 'short'], help='Position type')
    
    # Analyze
    subparsers.add_parser('analyze', help='Run AI analysis and compute metrics')
    
    # Run day
    subparsers.add_parser('run_day', help='Simulate daily iteration (update PnL, suggest trades)')
    
    # Report
    subparsers.add_parser('report', help='Show portfolio summary and PnL')
    
    # Legacy portfolio view
    subparsers.add_parser('portfolio', help='View portfolio (alias for report)')
    
    # Strategy suggestion
    strategy_parser = subparsers.add_parser('strategy', help='Get options strategy suggestions')
    strategy_parser.add_argument('--view', required=True, help='Market view (bullish/bearish/neutral)')
    strategy_parser.add_argument('--underlying', required=True, help='Underlying (NIFTY/BANKNIFTY)')
    strategy_parser.add_argument('--price', type=float, required=True, help='Current price')
    strategy_parser.add_argument('--volatility', default='medium', help='Volatility (low/medium/high)')
    
    # Sentiment analysis
    sentiment_parser = subparsers.add_parser('sentiment', help='Analyze market sentiment')
    sentiment_parser.add_argument('text', help='Text to analyze')
    sentiment_parser.add_argument('--json', action='store_true', help='Return simplified JSON format')
    sentiment_parser.add_argument('--full', action='store_true', help='Return full JSON format')
    sentiment_parser.add_argument('--underlying', default='NIFTY', help='Underlying symbol')
    
    # Income formulation
    income_parser = subparsers.add_parser('formulate_income', help='Formulate income generation strategy')
    income_parser.add_argument('--target', type=float, required=True, help='Target monthly income in ₹')
    income_parser.add_argument('--view', required=True, help='Market view (bullish/bearish/neutral)')
    income_parser.add_argument('--underlying', required=True, help='Underlying (NIFTY/BANKNIFTY)')
    income_parser.add_argument('--price', type=float, required=True, help='Current price')
    income_parser.add_argument('--volatility', default='medium', help='Volatility (low/medium/high)')
    income_parser.add_argument('--risk', default='medium', help='Risk tolerance (low/medium/high)')
    
    # Simulation commands
    sim_start_parser = subparsers.add_parser('sim_start', help='Start simulation')
    sim_start_parser.add_argument('--date', help='Start date (ISO format, optional)')
    
    subparsers.add_parser('sim_run_day', help='Run one day of simulation')
    
    sim_trade_parser = subparsers.add_parser('sim_execute_trade', help='Execute trade in simulation')
    sim_trade_parser.add_argument('basket', help='Basket name')
    sim_trade_parser.add_argument('symbol', help='Symbol')
    sim_trade_parser.add_argument('quantity', type=int, help='Quantity')
    sim_trade_parser.add_argument('price', type=float, help='Price')
    sim_trade_parser.add_argument('type', choices=['long', 'short'], help='Position type')
    
    sim_hedge_parser = subparsers.add_parser('sim_log_hedge', help='Log hedging action')
    sim_hedge_parser.add_argument('description', help='Hedging action description')
    
    subparsers.add_parser('sim_summary', help='Show simulation summary')
    subparsers.add_parser('sim_stop', help='Stop simulation')
    
    args = parser.parse_args()
    cli = CLI()
    
    if args.command == 'add_trade':
        cli.add_trade(args)
    elif args.command == 'analyze':
        cli.analyze(args)
    elif args.command == 'run_day':
        cli.run_day(args)
    elif args.command == 'report':
        cli.report(args)
    elif args.command == 'portfolio':
        cli.view_portfolio(args)
    elif args.command == 'strategy':
        cli.suggest_strategy(args)
    elif args.command == 'sentiment':
        cli.analyze_sentiment(args)
    elif args.command == 'formulate_income':
        cli.formulate_income(args)
    elif args.command == 'sim_start':
        cli.sim_start(args)
    elif args.command == 'sim_run_day':
        cli.sim_run_day(args)
    elif args.command == 'sim_execute_trade':
        cli.sim_execute_trade(args)
    elif args.command == 'sim_log_hedge':
        cli.sim_log_hedge(args)
    elif args.command == 'sim_summary':
        cli.sim_summary(args)
    elif args.command == 'sim_stop':
        cli.sim_stop(args)
    else:
        parser.print_help()
