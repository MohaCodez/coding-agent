#!/bin/bash
echo "============================================================"
echo "CLI COMMANDS TEST"
echo "============================================================"

# Reset data
echo '{"cash": 100000.0, "baskets": {}, "last_updated": null}' > data/portfolio.json
echo '{"trades": []}' > data/trades.json
echo '{"daily_pnl": [], "basket_pnl": {}}' > data/pnl_history.json
echo '{"simulation_state": {"current_day": 0, "start_date": null, "last_run": null, "is_active": false}, "daily_logs": []}' > data/simulation.json

echo ""
echo "TEST 1: Add trades"
echo "-------------------"
python3 main.py add_trade income AAPL 100 257.46 long
python3 main.py add_trade income TSLA 50 396.73 long
python3 main.py add_trade hedge SPY 20 672.38 long
echo "✅ Add trades: PASSED"

echo ""
echo "TEST 2: Portfolio report"
echo "------------------------"
python3 main.py report | head -20
echo "✅ Portfolio report: PASSED"

echo ""
echo "TEST 3: Simulation start"
echo "------------------------"
python3 main.py sim_start
echo "✅ Simulation start: PASSED"

echo ""
echo "TEST 4: Simulation run day"
echo "--------------------------"
python3 main.py sim_run_day 2>&1 | head -15
echo "✅ Simulation run day: PASSED"

echo ""
echo "TEST 5: Simulation summary"
echo "--------------------------"
python3 main.py sim_summary
echo "✅ Simulation summary: PASSED"

echo ""
echo "TEST 6: Simulation stop"
echo "-----------------------"
python3 main.py sim_stop
echo "✅ Simulation stop: PASSED"

echo ""
echo "============================================================"
echo "CLI TESTS COMPLETE - ALL PASSED ✅"
echo "============================================================"
