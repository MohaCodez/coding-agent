# main.py

## Purpose
Entry point for the Local Indian Options Trading Analyst CLI application.

## Usage

```bash
python main.py <command> [options]
```

## Commands Overview

| Command | Description |
|---------|-------------|
| `add` | Add position to portfolio |
| `portfolio` | View portfolio with AI analysis |
| `strategy` | Get options strategy suggestions |
| `sentiment` | Analyze market sentiment |
| `pnl` | Calculate and save PnL |
| `risk` | Portfolio risk analysis |

## Examples

### Add Position
```bash
python main.py add NIFTY24MAR21000CE 50 150.5 long
python main.py add BANKNIFTY24MAR45000PE 25 200.0 short
```

### View Portfolio
```bash
python main.py portfolio
```

### Strategy Suggestions
```bash
python main.py strategy --view bullish --underlying NIFTY --price 21500 --volatility medium
python main.py strategy --view bearish --underlying BANKNIFTY --price 45000 --volatility high
```

### Sentiment Analysis
```bash
python main.py sentiment "RBI maintains repo rate, signals dovish stance"
python main.py sentiment "FII selling continues, markets under pressure"
```

### PnL Calculation
```bash
python main.py pnl
```

### Risk Analysis
```bash
python main.py risk
```

## Help
```bash
python main.py --help
python main.py add --help
python main.py strategy --help
```

## Prerequisites
1. Install Ollama: https://ollama.ai
2. Pull Qwen model: `ollama pull qwen2.5:3b`
3. Install dependencies: `pip install -r requirements.txt`

## Architecture Flow
```
main.py
  ↓
modules/cli/commands.py (CLI logic)
  ↓
modules/analytics/* (Portfolio, Strategy, Risk)
modules/ai/* (Qwen interface, Sentiment)
  ↓
utils/* (File I/O, Market data)
  ↓
data/* (Persistent storage)
```
