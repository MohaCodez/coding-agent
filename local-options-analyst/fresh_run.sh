#!/bin/bash
set -e

echo "============================================================"
echo "FRESH RUN - Options Trading Analyst"
echo "Using Real Yahoo Finance Data"
echo "============================================================"
echo ""

# Clean slate
echo "Step 1: Resetting all data..."
echo '{"cash": 100000.0, "baskets": {}, "last_updated": null}' > data/portfolio.json
echo '{"trades": []}' > data/trades.json
echo '{"daily_pnl": [], "basket_pnl": {}}' > data/pnl_history.json
echo '{"simulation_state": {"current_day": 0, "start_date": null, "last_run": null, "is_active": false}, "daily_logs": []}' > data/simulation.json
rm -f data/market_data/daily_snapshots/*.json 2>/dev/null || true
echo "✓ Data reset complete"
echo ""

# Fetch current market prices
echo "Step 2: Fetching current market prices from Yahoo Finance..."
python3 << 'PYEOF'
from utils.market_fetcher import fetch_yahoo_data
import json

symbols = ['AAPL', 'MSFT', 'GOOGL', 'SPY']
print("\nCurrent Market Prices:")
print("-" * 50)
prices = {}
for symbol in symbols:
    data = fetch_yahoo_data(symbol)
    prices[symbol] = data['price']
    change = data['change']
    pct = data['pChange']
    print(f"{symbol:6} ${data['price']:8.2f}  Change: ${change:+7.2f} ({pct:+.2f}%)")

# Save for reference
with open('/tmp/current_prices.json', 'w') as f:
    json.dump(prices, f)
PYEOF
echo ""

# Add positions
echo "Step 3: Building portfolio..."
echo ""
echo "Adding positions at current market prices:"

# Read prices
AAPL_PRICE=$(python3 -c "import json; print(json.load(open('/tmp/current_prices.json'))['AAPL'])")
MSFT_PRICE=$(python3 -c "import json; print(json.load(open('/tmp/current_prices.json'))['MSFT'])")
GOOGL_PRICE=$(python3 -c "import json; print(json.load(open('/tmp/current_prices.json'))['GOOGL'])")
SPY_PRICE=$(python3 -c "import json; print(json.load(open('/tmp/current_prices.json'))['SPY'])")

echo "  Income Basket:"
python3 main.py add_trade income AAPL 50 $AAPL_PRICE long
python3 main.py add_trade income MSFT 30 $MSFT_PRICE long

echo ""
echo "  Growth Basket:"
python3 main.py add_trade growth GOOGL 10 $GOOGL_PRICE long

echo ""
echo "  Hedge Basket:"
python3 main.py add_trade hedge SPY 15 $SPY_PRICE long

echo ""
echo "✓ Portfolio built"
echo ""

# View portfolio
echo "Step 4: Portfolio Report"
echo "============================================================"
python3 main.py report
echo ""

# Start simulation
echo "Step 5: Starting Simulation"
echo "============================================================"
python3 main.py sim_start
echo ""

# Run 3 days
echo "Step 6: Running 3-Day Simulation"
echo "============================================================"
for day in 1 2 3; do
    echo ""
    echo "--- Running Day $day ---"
    python3 main.py sim_run_day 2>&1 | grep -A 20 "=== Day"
    sleep 1
done

echo ""
echo "Step 7: Simulation Summary"
echo "============================================================"
python3 main.py sim_summary

echo ""
echo "Step 8: Final Portfolio Report"
echo "============================================================"
python3 main.py report

echo ""
echo "============================================================"
echo "FRESH RUN COMPLETE ✓"
echo "============================================================"
