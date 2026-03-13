# Phase 3: AI Prompts - Implementation Summary

## Completed Features

### 1. Enhanced Portfolio Prompt ✓

**File**: `prompts/portfolio_prompt.txt`

**Capabilities**:
- Analyzes portfolio.json AND trades.json together
- Computes PnL with realized/unrealized breakdown
- Evaluates allocation across baskets
- Assesses risk via Greeks analysis
- Provides specific rebalancing recommendations

**Input Variables**:
- `{portfolio_data}` - Current positions, valuation, allocations, Greeks
- `{trade_history}` - Recent trade history for pattern analysis

**Output Sections**:
1. PnL Summary - Metrics and trends
2. Allocation Review - Current vs optimal
3. Risk Profile - Greeks and exposure
4. Rebalancing Actions - Specific trades to execute

### 2. Enhanced Options Strategy Prompt ✓

**File**: `prompts/options_strategy_prompt.txt`

**Capabilities**:
- Formulates income generation strategies (credit spreads, iron condors, covered calls)
- Suggests hedging trades for risk management
- Returns structured JSON output

**Input Variables**:
- `{target_income}` - Monthly income goal
- `{portfolio_summary}` - Current portfolio state
- `{market_view}` - Bullish/bearish/neutral
- `{underlying}` - NIFTY/BANKNIFTY
- `{current_price}` - Spot price
- `{volatility}` - Low/medium/high
- `{risk_tolerance}` - Low/medium/high

**JSON Output Structure**:
```json
{
  "suggested_trades": [
    {
      "strategy_name": "Bull Call Spread",
      "underlying": "NIFTY",
      "expiry": "28-MAR-2024",
      "legs": [...],
      "net_premium": -2500,
      "max_profit": 7500,
      "max_loss": 2500,
      "breakeven": 21050,
      "margin_required": 15000,
      "expected_income": 5000,
      "probability_of_profit": 0.65
    }
  ],
  "hedging_recommendations": [...],
  "expected_income": {
    "monthly": 15000,
    "annualized": 180000,
    "return_on_capital": 0.18
  },
  "risk_summary": {
    "total_margin": 45000,
    "max_loss": 12500,
    "risk_reward_ratio": 2.4
  }
}
```

### 3. Enhanced Sentiment Prompt ✓

**File**: `prompts/sentiment_prompt.txt`

**Capabilities**:
- Analyzes financial news/text for Indian markets
- Returns sentiment score per underlying (-1 to 1)
- Uses ONLY local input data (no external assumptions)
- Provides trading implications

**Input Variables**:
- `{text}` - News/text to analyze

**JSON Output Structure**:
```json
{
  "overall_sentiment": {
    "classification": "bullish",
    "score": 0.65,
    "confidence": 0.80
  },
  "underlying_sentiment": {
    "NIFTY": {
      "score": 0.60,
      "impact": "Positive due to...",
      "confidence": 0.75
    },
    "BANKNIFTY": {
      "score": 0.70,
      "impact": "Strong positive...",
      "confidence": 0.85
    }
  },
  "key_factors": [...],
  "trading_implications": {
    "recommended_bias": "bullish",
    "strategies": [...],
    "risk_factors": [...]
  },
  "time_horizon": "short-term",
  "volatility_expectation": "decreasing"
}
```

**Scoring Guidelines**:
- +0.7 to +1.0: Strongly bullish
- +0.3 to +0.7: Moderately bullish
- -0.3 to +0.3: Neutral
- -0.7 to -0.3: Moderately bearish
- -1.0 to -0.7: Strongly bearish

## Module Updates

### options_strategy.py ✓
- Added `formulate_income_strategy()` method
- JSON parsing with `_parse_strategy_json()`
- Fallback structure for parsing failures

### sentiment.py ✓
- Refactored `analyze()` to return full JSON
- Added `analyze_text()` for formatted text output
- Enhanced `analyze_json()` for specific underlying extraction
- Added `_parse_sentiment_json()` with robust error handling
- Added `_format_sentiment_text()` for human-readable output

### commands.py ✓
- Updated `analyze()` to include trade history in prompt
- Enhanced `analyze_sentiment()` with `--full` flag
- Added `formulate_income` command for income strategy generation

## New CLI Commands

### formulate_income
Generate income strategies with structured JSON output:
```bash
python main.py formulate_income \
  --target 15000 \
  --view bullish \
  --underlying NIFTY \
  --price 21500 \
  --volatility medium \
  --risk medium
```

**Output**: Complete JSON with suggested trades, hedging, expected income, risk summary

### sentiment (enhanced)
```bash
# Text format (human-readable)
python main.py sentiment "RBI maintains dovish stance"

# Simplified JSON (specific underlying)
python main.py sentiment "FII selling continues" --json --underlying NIFTY

# Full JSON (all underlyings + implications)
python main.py sentiment "Market rally on positive earnings" --full
```

## Usage Examples

### 1. Portfolio Analysis with Trade History
```bash
python main.py add_trade income NIFTY24MAR21000CE 50 150.5 long
python main.py add_trade income NIFTY24MAR21200CE 50 120.0 short
python main.py analyze
# AI analyzes positions + recent trades for patterns
```

### 2. Income Strategy Formulation
```bash
python main.py formulate_income \
  --target 20000 \
  --view neutral \
  --underlying BANKNIFTY \
  --price 45000 \
  --volatility high \
  --risk low
# Returns JSON with iron condors, credit spreads, hedges
```

### 3. Sentiment Analysis
```bash
# Full analysis
python main.py sentiment "RBI cuts repo rate by 25bps, dovish on inflation" --full

# Quick score for NIFTY
python main.py sentiment "FII buying accelerates" --json --underlying NIFTY
```

## Key Features

1. **Structured JSON Output** - All prompts return parseable JSON for automation
2. **Local Data Only** - Sentiment uses only provided text, no external assumptions
3. **Comprehensive Analysis** - Portfolio prompt analyzes both positions and trade patterns
4. **Income Focus** - Strategy prompt optimized for income generation with risk management
5. **Multi-underlying Support** - Sentiment analyzes impact on NIFTY, BANKNIFTY, and stocks
6. **Robust Parsing** - Fallback structures for AI response parsing failures
7. **Flexible Output** - Text or JSON formats based on use case

## Prompt Design Principles

1. **Clear Instructions** - Explicit task breakdown and output format
2. **Structured Output** - JSON schemas for programmatic consumption
3. **Context Awareness** - Indian market specific (NSE/BSE, NIFTY, BANKNIFTY)
4. **Actionable Insights** - Specific strikes, quantities, strategies
5. **Risk Management** - Always include hedging and risk metrics
6. **Realistic Constraints** - Margin requirements, probability of profit

Phase 3 complete! All prompts are production-ready with structured JSON outputs.
