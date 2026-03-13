#!/usr/bin/env python3
"""Comprehensive test suite for Options Trading Analyst"""

import sys
import json
from datetime import datetime

# Test counter
tests_passed = 0
tests_failed = 0

def test(name):
    """Decorator for tests"""
    def decorator(func):
        def wrapper():
            global tests_passed, tests_failed
            try:
                print(f"\n{'='*60}")
                print(f"TEST: {name}")
                print('='*60)
                func()
                print(f"✅ PASSED: {name}")
                tests_passed += 1
            except Exception as e:
                print(f"❌ FAILED: {name}")
                print(f"Error: {e}")
                tests_failed += 1
        return wrapper
    return decorator

# Test 1: Yahoo Finance Stock Data
@test("Yahoo Finance - Stock Data Fetching")
def test_yahoo_stock_data():
    from utils.market_fetcher import fetch_yahoo_data
    
    symbols = ['AAPL', 'TSLA', 'SPY']
    for symbol in symbols:
        data = fetch_yahoo_data(symbol)
        assert data['symbol'] == symbol, f"Symbol mismatch: {data['symbol']}"
        assert data['price'] > 0, f"Invalid price: {data['price']}"
        assert data['source'] == 'Yahoo Finance', f"Wrong source: {data['source']}"
        print(f"  {symbol}: ${data['price']:.2f} ✓")

# Test 2: Option Chain Fetching
@test("Yahoo Finance - Option Chain Fetching")
def test_option_chain():
    from utils.market_fetcher import fetch_option_chain_yahoo
    
    data = fetch_option_chain_yahoo('AAPL')
    assert data['symbol'] == 'AAPL', "Symbol mismatch"
    assert len(data['strikes']) > 0, "No strikes found"
    assert 'expiry' in data, "No expiry date"
    assert len(data['available_expiries']) > 0, "No expiries available"
    
    print(f"  Strikes: {len(data['strikes'])}")
    print(f"  Expiry: {data['expiry']}")
    print(f"  Available expiries: {len(data['available_expiries'])}")
    
    # Check strike data
    strike = data['strikes'][0]
    assert 'strike' in strike, "Missing strike price"
    assert 'call_ltp' in strike or 'put_ltp' in strike, "Missing option prices"

# Test 3: Portfolio Management
@test("Portfolio - Add Positions")
def test_portfolio_add():
    from modules.analytics.portfolio import Portfolio
    from pathlib import Path
    
    # Reset portfolio
    portfolio_path = Path('data/portfolio.json')
    portfolio_path.write_text('{"cash": 100000.0, "baskets": {}, "last_updated": null}')
    
    portfolio = Portfolio()
    
    # Add positions
    portfolio.add_position('test_basket', 'AAPL', 100, 250.0, 'long')
    portfolio.add_position('test_basket', 'TSLA', 50, 400.0, 'long')
    
    positions = portfolio.get_positions('test_basket')
    assert len(positions) == 2, f"Expected 2 positions, got {len(positions)}"
    assert positions[0]['symbol'] == 'AAPL', "First position should be AAPL"
    assert positions[1]['symbol'] == 'TSLA', "Second position should be TSLA"
    
    print(f"  Added 2 positions to test_basket ✓")

# Test 4: PnL Calculation
@test("Portfolio - PnL Calculation")
def test_pnl_calculation():
    from modules.analytics.portfolio import Portfolio
    
    portfolio = Portfolio()
    
    # Mock prices
    current_prices = {
        'AAPL': 260.0,  # +10 from 250
        'TSLA': 390.0   # -10 from 400
    }
    
    pnl = portfolio.calculate_pnl(current_prices, 'test_basket')
    expected_pnl = (260-250)*100 + (390-400)*50  # 1000 - 500 = 500
    
    assert abs(pnl - expected_pnl) < 0.01, f"PnL mismatch: {pnl} vs {expected_pnl}"
    print(f"  PnL: ${pnl:.2f} (Expected: ${expected_pnl:.2f}) ✓")

# Test 5: Greeks Calculation
@test("Risk Analytics - Greeks Calculation")
def test_greeks():
    from modules.analytics.risk import RiskAnalyzer
    
    analyzer = RiskAnalyzer()
    
    positions = [
        {'symbol': 'AAPL', 'quantity': 100, 'entry_price': 250, 'type': 'long'},
        {'symbol': 'TSLA', 'quantity': 50, 'entry_price': 400, 'type': 'short'}
    ]
    
    greeks = analyzer.calculate_portfolio_greeks(positions)
    
    assert 'delta' in greeks, "Missing delta"
    assert 'gamma' in greeks, "Missing gamma"
    assert 'theta' in greeks, "Missing theta"
    assert 'vega' in greeks, "Missing vega"
    
    print(f"  Delta: {greeks['delta']}")
    print(f"  Gamma: {greeks['gamma']}")
    print(f"  Theta: {greeks['theta']}")
    print(f"  Vega: {greeks['vega']}")

# Test 6: Basket System
@test("Modular Baskets - Custom Basket Creation")
def test_custom_basket():
    from modules.baskets.base import BaseBasket, BasketFactory
    
    class TestBasket(BaseBasket):
        def validate_position(self, symbol, quantity, price, position_type):
            return True
        def get_target_allocation(self):
            return 0.3
    
    BasketFactory.register_basket_type('test', TestBasket)
    basket = BasketFactory.create_basket('test', 'my_test')
    
    assert basket.name == 'my_test', "Basket name mismatch"
    assert basket.get_target_allocation() == 0.3, "Allocation mismatch"
    
    print(f"  Custom basket created: {basket.name} ✓")
    print(f"  Target allocation: {basket.get_target_allocation():.0%} ✓")

# Test 7: Strategy System
@test("Modular Strategies - Custom Strategy Creation")
def test_custom_strategy():
    from modules.strategies.base import BaseStrategy, StrategyFactory
    
    class TestStrategy(BaseStrategy):
        def generate_signals(self, market_data, portfolio_state):
            return {'strategy': 'test', 'signals': [{'action': 'buy'}]}
        def get_risk_parameters(self):
            return {'max_loss': 5000}
    
    StrategyFactory.register_strategy_type('test', TestStrategy)
    strategy = StrategyFactory.create_strategy('test', 'my_test')
    
    signals = strategy.generate_signals({}, {})
    risk = strategy.get_risk_parameters()
    
    assert signals['strategy'] == 'test', "Strategy name mismatch"
    assert risk['max_loss'] == 5000, "Risk parameter mismatch"
    
    print(f"  Custom strategy created: {strategy.name} ✓")
    print(f"  Signals generated: {signals} ✓")

# Test 8: Simulation Engine
@test("Simulation Engine - State Management")
def test_simulation():
    from modules.simulation.engine import SimulationEngine
    from pathlib import Path
    
    # Reset simulation
    sim_path = Path('data/simulation.json')
    sim_path.write_text('{"simulation_state": {"current_day": 0, "start_date": null, "last_run": null, "is_active": false}, "daily_logs": []}')
    
    sim = SimulationEngine('data')
    
    # Start simulation
    result = sim.start_simulation()
    assert result['status'] == 'started', "Simulation didn't start"
    
    # Check state
    assert sim.state['simulation_state']['is_active'] == True, "Simulation not active"
    
    print(f"  Simulation started: {result['date'][:19]} ✓")
    
    # Stop simulation
    result = sim.stop_simulation()
    assert result['status'] == 'stopped', "Simulation didn't stop"
    
    print(f"  Simulation stopped ✓")

# Test 9: Data Persistence
@test("Data Persistence - JSON Files")
def test_data_persistence():
    from pathlib import Path
    
    files = [
        'data/portfolio.json',
        'data/trades.json',
        'data/pnl_history.json',
        'data/simulation.json'
    ]
    
    for file in files:
        path = Path(file)
        assert path.exists(), f"File not found: {file}"
        
        # Verify it's valid JSON
        with open(path) as f:
            data = json.load(f)
        
        print(f"  {file}: Valid JSON ✓")

# Test 10: Real-time Price Integration
@test("Integration - Real Prices in Portfolio")
def test_real_prices_integration():
    from utils.market_fetcher import get_real_prices
    
    symbols = ['AAPL', 'TSLA', 'SPY']
    prices = get_real_prices(symbols)
    
    for symbol in symbols:
        assert symbol in prices, f"Missing price for {symbol}"
        assert prices[symbol] > 0, f"Invalid price for {symbol}: {prices[symbol]}"
        print(f"  {symbol}: ${prices[symbol]:.2f} ✓")

# Run all tests
if __name__ == '__main__':
    print("\n" + "="*60)
    print("OPTIONS TRADING ANALYST - TEST SUITE")
    print("="*60)
    
    test_yahoo_stock_data()
    test_option_chain()
    test_portfolio_add()
    test_pnl_calculation()
    test_greeks()
    test_custom_basket()
    test_custom_strategy()
    test_simulation()
    test_data_persistence()
    test_real_prices_integration()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"Total: {tests_passed + tests_failed}")
    print(f"Success Rate: {tests_passed/(tests_passed+tests_failed)*100:.1f}%")
    print("="*60)
    
    sys.exit(0 if tests_failed == 0 else 1)
