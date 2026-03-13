# market_fetcher.py

## Purpose
Fetch live market data from NSE (National Stock Exchange). Currently contains placeholder functions for integration.

## Functions

### fetch_nse_data(symbol)
Fetch current price and market data for a symbol.

**Inputs:**
- `symbol`: Stock/index symbol (e.g., "NIFTY", "RELIANCE")

**Outputs:**
```json
{
  "symbol": "NIFTY",
  "price": 21500.0,
  "timestamp": "2026-03-08T15:30:00",
  "change": 150.5,
  "change_percent": 0.7
}
```

**Example:**
```python
from utils.market_fetcher import fetch_nse_data

data = fetch_nse_data("NIFTY")
print(f"NIFTY: ₹{data['price']}")
```

### fetch_option_chain(symbol)
Fetch option chain data for an underlying.

**Inputs:**
- `symbol`: Underlying symbol (e.g., "NIFTY", "BANKNIFTY")

**Outputs:**
```json
{
  "symbol": "NIFTY",
  "strikes": [
    {
      "strike": 21000,
      "call_ltp": 150.5,
      "put_ltp": 25.0,
      "call_oi": 5000000,
      "put_oi": 3000000
    }
  ],
  "timestamp": "2026-03-08T15:30:00"
}
```

**Example:**
```python
from utils.market_fetcher import fetch_option_chain

chain = fetch_option_chain("NIFTY")
for strike in chain['strikes']:
    print(f"Strike {strike['strike']}: CE ₹{strike['call_ltp']}, PE ₹{strike['put_ltp']}")
```

## Integration Guide

### Option 1: NSE Official API
- Register for NSE API access
- Use authentication tokens
- Rate limits apply

### Option 2: Web Scraping
- Use requests + BeautifulSoup
- Parse NSE website option chain
- Add delays to avoid blocking

### Option 3: Third-party Data Providers
- Zerodha Kite API
- Upstox API
- Dhan API
- Fyers API

## Implementation Notes
Current functions return mock data. Replace with actual API calls:

```python
import requests

def fetch_nse_data(symbol):
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return response.json()
```

## Use Cases
- Real-time PnL calculation
- Option chain analysis
- Strategy backtesting
- Market data snapshots
