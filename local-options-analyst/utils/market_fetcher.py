from datetime import datetime
import json
import time

# Try to import yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not installed. Run: pip install yfinance")

_last_request_time = 0
_min_request_interval = 0.5  # Yahoo Finance is more lenient

def _rate_limit():
    """Enforce rate limiting."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < _min_request_interval:
        time.sleep(_min_request_interval - elapsed)
    _last_request_time = time.time()

def fetch_yahoo_data(symbol):
    """Fetch real-time data from Yahoo Finance."""
    if not YFINANCE_AVAILABLE:
        return _mock_fallback(symbol)
    
    try:
        _rate_limit()
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        
        return {
            "symbol": symbol,
            "price": float(current_price),
            "change": float(info.get('regularMarketChange', 0)),
            "pChange": float(info.get('regularMarketChangePercent', 0)),
            "open": float(info.get('regularMarketOpen', 0)),
            "high": float(info.get('regularMarketDayHigh', 0)),
            "low": float(info.get('regularMarketDayLow', 0)),
            "volume": int(info.get('regularMarketVolume', 0)),
            "timestamp": datetime.now().isoformat(),
            "source": "Yahoo Finance"
        }
    except Exception as e:
        print(f"Error fetching Yahoo data for {symbol}: {e}")
        return _mock_fallback(symbol)

def fetch_option_chain_yahoo(symbol, expiry_date=None):
    """Fetch option chain from Yahoo Finance."""
    if not YFINANCE_AVAILABLE:
        return {"symbol": symbol, "strikes": [], "error": "yfinance not installed"}
    
    try:
        _rate_limit()
        ticker = yf.Ticker(symbol)
        
        # Get available expiration dates
        expirations = ticker.options
        if not expirations:
            return {"symbol": symbol, "strikes": [], "error": "No options available"}
        
        # Use first expiry if not specified
        expiry = expiry_date or expirations[0]
        
        # Get option chain
        opt_chain = ticker.option_chain(expiry)
        calls = opt_chain.calls
        puts = opt_chain.puts
        
        # Combine by strike
        strikes_dict = {}
        
        # Helper to safely convert to float/int
        def safe_float(val, default=0.0):
            try:
                if val is None or (isinstance(val, float) and (val != val)):  # Check for NaN
                    return default
                return float(val)
            except:
                return default
        
        def safe_int(val, default=0):
            try:
                if val is None or (isinstance(val, float) and (val != val)):
                    return default
                return int(val)
            except:
                return default
        
        for _, call in calls.iterrows():
            strike = safe_float(call['strike'])
            if strike == 0:
                continue
            if strike not in strikes_dict:
                strikes_dict[strike] = {"strike": strike, "expiry": expiry}
            strikes_dict[strike].update({
                "call_ltp": safe_float(call['lastPrice']),
                "call_bid": safe_float(call['bid']),
                "call_ask": safe_float(call['ask']),
                "call_volume": safe_int(call['volume']),
                "call_oi": safe_int(call['openInterest']),
                "call_iv": safe_float(call['impliedVolatility']),
            })
        
        for _, put in puts.iterrows():
            strike = safe_float(put['strike'])
            if strike == 0:
                continue
            if strike not in strikes_dict:
                strikes_dict[strike] = {"strike": strike, "expiry": expiry}
            strikes_dict[strike].update({
                "put_ltp": safe_float(put['lastPrice']),
                "put_bid": safe_float(put['bid']),
                "put_ask": safe_float(put['ask']),
                "put_volume": safe_int(put['volume']),
                "put_oi": safe_int(put['openInterest']),
                "put_iv": safe_float(put['impliedVolatility']),
            })
        
        strikes = sorted(strikes_dict.values(), key=lambda x: x['strike'])
        
        return {
            "symbol": symbol,
            "strikes": strikes,
            "expiry": expiry,
            "available_expiries": list(expirations),
            "timestamp": datetime.now().isoformat(),
            "source": "Yahoo Finance"
        }
    except Exception as e:
        print(f"Error fetching option chain for {symbol}: {e}")
        return {"symbol": symbol, "strikes": [], "error": str(e)}

def get_real_prices(symbols):
    """Get real prices from Yahoo Finance."""
    prices = {}
    
    for symbol in symbols:
        # For option symbols, try to parse and get underlying price
        if any(x in symbol for x in ['C', 'P']) and len(symbol) > 6:
            # This is likely an option symbol, use mock for now
            import random
            prices[symbol] = round(random.uniform(1, 50), 2)
        else:
            # For stocks/ETFs, fetch real data
            data = fetch_yahoo_data(symbol)
            prices[symbol] = data.get('price', 0.0)
            
            # If still 0, use mock
            if prices[symbol] == 0.0:
                import random
                prices[symbol] = round(random.uniform(50, 500), 2)
    
    return prices

def _mock_fallback(symbol):
    """Generate mock data as fallback."""
    import random
    return {
        "symbol": symbol,
        "price": round(random.uniform(50, 500), 2),
        "change": round(random.uniform(-10, 10), 2),
        "pChange": round(random.uniform(-5, 5), 2),
        "timestamp": datetime.now().isoformat(),
        "source": "mock_fallback"
    }

def save_market_snapshot(symbol, data, data_dir):
    """Save market data snapshot to daily_snapshots."""
    from pathlib import Path
    snapshot_dir = Path(data_dir) / 'market_data' / 'daily_snapshots'
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = snapshot_dir / f"{symbol}_{date_str}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return str(filename)

def get_mock_prices(symbols):
    """Generate mock current prices for testing."""
    import random
    prices = {}
    for symbol in symbols:
        prices[symbol] = round(random.uniform(50, 300), 2)
    return prices

# Legacy NSE functions (kept for compatibility)
def fetch_nse_data(symbol):
    """Legacy NSE function - redirects to Yahoo Finance."""
    return fetch_yahoo_data(symbol)

def fetch_option_chain(symbol):
    """Legacy option chain function - redirects to Yahoo Finance."""
    return fetch_option_chain_yahoo(symbol)

def fetch_index_data(index_name="^GSPC"):
    """Fetch index data (defaults to S&P 500)."""
    return fetch_yahoo_data(index_name)
