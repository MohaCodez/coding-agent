# Real Data Ingestion Guide

## Current State: Mock Data Only

The project currently uses **mock/simulated data** for testing. Here's how to integrate real market data:

---

## Option 1: NSE Official Website (Free, No API Key)

### Implementation

```python
# In utils/market_fetcher.py

import requests
from datetime import datetime

def fetch_nse_data(symbol):
    """Fetch real data from NSE website."""
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        session = requests.Session()
        # First request to get cookies
        session.get("https://www.nseindia.com", headers=headers)
        
        # Actual data request
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "symbol": symbol,
            "price": data['priceInfo']['lastPrice'],
            "change": data['priceInfo']['change'],
            "volume": data['preOpenMarket']['totalTradedVolume'],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error fetching NSE data: {e}")
        return {"symbol": symbol, "price": 0.0, "error": str(e)}

def fetch_option_chain(symbol):
    """Fetch option chain from NSE."""
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        strikes = []
        for record in data['records']['data']:
            strikes.append({
                "strike": record['strikePrice'],
                "call_ltp": record.get('CE', {}).get('lastPrice', 0),
                "put_ltp": record.get('PE', {}).get('lastPrice', 0),
                "call_oi": record.get('CE', {}).get('openInterest', 0),
                "put_oi": record.get('PE', {}).get('openInterest', 0),
            })
        
        return {
            "symbol": symbol,
            "strikes": strikes,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error fetching option chain: {e}")
        return {"symbol": symbol, "strikes": [], "error": str(e)}
```

**Pros**: Free, no API key needed  
**Cons**: Rate limits, may block if too many requests

---

## Option 2: Broker APIs (Recommended for Production)

### Zerodha Kite API

```python
from kiteconnect import KiteConnect

def setup_kite():
    """Setup Kite Connect."""
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    kite = KiteConnect(api_key=api_key)
    
    # Login flow (one-time)
    # Get request token from login URL
    # kite.generate_session(request_token, api_secret=api_secret)
    
    return kite

def fetch_nse_data_kite(symbol):
    """Fetch data using Kite API."""
    kite = setup_kite()
    
    try:
        quote = kite.quote(f"NSE:{symbol}")
        data = quote[f"NSE:{symbol}"]
        
        return {
            "symbol": symbol,
            "price": data['last_price'],
            "change": data['change'],
            "volume": data['volume'],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"symbol": symbol, "price": 0.0, "error": str(e)}

def fetch_option_chain_kite(symbol, expiry):
    """Fetch option chain using Kite."""
    kite = setup_kite()
    
    try:
        instruments = kite.instruments("NFO")
        options = [i for i in instruments 
                   if i['name'] == symbol 
                   and i['expiry'] == expiry
                   and i['instrument_type'] in ['CE', 'PE']]
        
        strikes = {}
        for opt in options:
            strike = opt['strike']
            if strike not in strikes:
                strikes[strike] = {}
            
            quote = kite.quote(f"NFO:{opt['tradingsymbol']}")
            opt_data = quote[f"NFO:{opt['tradingsymbol']}"]
            
            if opt['instrument_type'] == 'CE':
                strikes[strike]['call_ltp'] = opt_data['last_price']
                strikes[strike]['call_oi'] = opt_data['oi']
            else:
                strikes[strike]['put_ltp'] = opt_data['last_price']
                strikes[strike]['put_oi'] = opt_data['oi']
        
        return {
            "symbol": symbol,
            "strikes": [{"strike": k, **v} for k, v in strikes.items()],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"symbol": symbol, "strikes": [], "error": str(e)}
```

**Setup**:
```bash
pip install kiteconnect
```

**Pros**: Official, reliable, real-time  
**Cons**: Requires account, API subscription

---

## Option 3: Other Broker APIs

### Upstox API
```bash
pip install upstox-python
```

### Dhan API
```bash
pip install dhanhq
```

### Fyers API
```bash
pip install fyers-apiv2
```

Similar implementation pattern as Kite.

---

## Option 4: CSV Import (Historical Data)

```python
import pandas as pd

def import_historical_data(csv_path):
    """Import historical option data from CSV."""
    df = pd.read_csv(csv_path)
    
    # Expected columns: date, symbol, strike, type, ltp, oi
    data = []
    for _, row in df.iterrows():
        data.append({
            "date": row['date'],
            "symbol": row['symbol'],
            "strike": row['strike'],
            "type": row['type'],  # CE/PE
            "ltp": row['ltp'],
            "oi": row['oi']
        })
    
    return data

def load_historical_prices(csv_path):
    """Load historical prices for backtesting."""
    df = pd.read_csv(csv_path, parse_dates=['date'])
    return df.set_index('date').to_dict('index')
```

**Pros**: Good for backtesting  
**Cons**: Not real-time

---

## Option 5: Web Scraping (Last Resort)

```python
from bs4 import BeautifulSoup
import requests

def scrape_nse_option_chain(symbol):
    """Scrape NSE website (use carefully, may violate ToS)."""
    url = f"https://www.nseindia.com/option-chain"
    
    # Add delays, respect robots.txt
    # Implement proper error handling
    # This is just a skeleton
    
    # NOT RECOMMENDED - Use official APIs instead
    pass
```

**Pros**: No API key needed  
**Cons**: Fragile, may violate ToS, can break anytime

---

## Recommended Integration Steps

### Step 1: Choose Data Source
- **For Testing**: Keep mock data (current)
- **For Production**: Use broker API (Zerodha/Upstox)
- **For Free Access**: NSE website scraping (with caution)

### Step 2: Update market_fetcher.py
Replace mock functions with real implementations.

### Step 3: Add Configuration
```python
# In kiro-config.json
{
  "data_source": "kite",  # or "nse", "mock"
  "api_key": "your_key",
  "api_secret": "your_secret",
  "update_interval": 60  # seconds
}
```

### Step 4: Add Caching
```python
import time

_cache = {}
_cache_ttl = 60  # seconds

def fetch_with_cache(symbol):
    """Fetch with caching to avoid rate limits."""
    now = time.time()
    
    if symbol in _cache:
        data, timestamp = _cache[symbol]
        if now - timestamp < _cache_ttl:
            return data
    
    data = fetch_nse_data(symbol)
    _cache[symbol] = (data, now)
    return data
```

### Step 5: Add Scheduled Updates
```python
import schedule
import time

def update_market_data():
    """Scheduled market data update."""
    symbols = get_all_symbols_from_portfolio()
    for symbol in symbols:
        data = fetch_nse_data(symbol)
        save_to_database(data)

# Run every minute during market hours
schedule.every(1).minutes.do(update_market_data)

while True:
    schedule.run_pending()
    time.sleep(1)
```

---

## Current vs. Real Data Comparison

| Aspect | Current (Mock) | With Real Data |
|--------|----------------|----------------|
| Prices | Random 50-300 | Actual NSE prices |
| Option Chain | Empty | Full chain with OI |
| Updates | Manual | Automatic/scheduled |
| Accuracy | N/A | Real-time |
| Cost | Free | Free to ₹2000/month |

---

## Quick Start: Add NSE Data (5 minutes)

1. **Update market_fetcher.py** with NSE implementation above
2. **Test it**:
   ```bash
   python3 -c "
   from utils.market_fetcher import fetch_nse_data
   data = fetch_nse_data('RELIANCE')
   print(data)
   "
   ```
3. **Replace get_mock_prices** calls with real fetches
4. **Done!**

---

## Dependencies for Real Data

```bash
# For NSE scraping
pip install requests beautifulsoup4

# For broker APIs
pip install kiteconnect  # Zerodha
pip install upstox-python  # Upstox
pip install dhanhq  # Dhan

# For CSV import
pip install pandas

# For scheduling
pip install schedule
```

---

## Important Notes

1. **Rate Limits**: NSE website has rate limits, add delays
2. **Market Hours**: Only fetch during 9:15 AM - 3:30 PM IST
3. **Holidays**: Check for market holidays
4. **Error Handling**: Always handle network errors
5. **Caching**: Cache data to reduce API calls
6. **Legal**: Ensure compliance with data provider ToS

---

## Summary

**Current**: Mock data for testing ✓  
**Next Step**: Choose and integrate real data source  
**Recommended**: Start with NSE website, move to broker API for production
