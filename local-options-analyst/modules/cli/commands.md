# commands.py

## Purpose
CLI interface for the Local Indian Options Trading Analyst. Handles all user commands and orchestrates modules.

## Commands

### 1. add
Add position to portfolio

**Inputs:**
- `symbol`: Option symbol (e.g., NIFTY24MAR21000CE)
- `quantity`: Number of contracts
- `price`: Entry price in ₹
- `type`: "long" or "short"

**Output:** Confirmation message

**Example:**
```bash
python main.py add NIFTY24MAR21000CE 50 150.5 long
# ✓ Added long position: NIFTY24MAR21000CE x50 @ ₹150.5
```

### 2. portfolio
View portfolio with AI analysis

**Inputs:** None

**Output:** 
- List of all positions
- AI-powered portfolio analysis from Qwen 3B

**Example:**
```bash
python main.py portfolio
# === Portfolio ===
# 1. NIFTY24MAR21000CE | long | Qty: 50 | Entry: ₹150.5
# 
# === AI Analysis ===
# Your portfolio shows bullish bias with net positive delta...
```

### 3. strategy
Get AI-powered options strategy suggestions

**Inputs:**
- `--view`: Market view (bullish/bearish/neutral)
- `--underlying`: NIFTY/BANKNIFTY/stock
- `--price`: Current spot price
- `--volatility`: low/medium/high (default: medium)

**Output:** 3 strategy suggestions with details

**Example:**
```bash
python main.py strategy --view bullish --underlying NIFTY --price 21500 --volatility medium
# === Strategy Suggestions ===
# 1. Bull Call Spread...
```

### 4. sentiment
Analyze market sentiment from text

**Inputs:**
- `text`: News/tweet/report to analyze

**Output:** Sentiment analysis with trading implications

**Example:**
```bash
python main.py sentiment "RBI maintains repo rate, dovish stance"
# === Sentiment Analysis ===
# Sentiment: Bullish (70% confidence)...
```

### 5. pnl
Calculate and save daily PnL

**Inputs:** None (uses current market prices)

**Output:** Total PnL, saved to pnl_history.json

**Example:**
```bash
python main.py pnl
# === PnL ===
# Total PnL: ₹12,250.00
```

### 6. risk
Portfolio risk analysis

**Inputs:** None

**Output:** Greeks, VaR, margin requirements

**Example:**
```bash
python main.py risk
# === Risk Analysis ===
# Greeks: {"delta": 25.5, "gamma": 0.05, ...}
# Margin: {"margin": 45000.0}
```

## Architecture
```
CLI → Portfolio/Strategy/Sentiment/Risk Modules → Qwen AI → Output
     ↓
  Data Storage (JSON files)
```
