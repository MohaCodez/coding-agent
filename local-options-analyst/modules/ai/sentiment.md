# sentiment.py

## Purpose
Analyzes market sentiment from news, social media, or text using Qwen 3B AI model.

## Inputs
- `text`: Market-related text to analyze (news, tweets, reports)

## Outputs
- Sentiment classification: Bullish/Bearish/Neutral
- Confidence percentage
- Key factors identified
- Impact on Nifty/Bank Nifty
- Trading implications

## Usage Examples

```python
from modules.ai.sentiment import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Analyze news
text = "RBI maintains repo rate at 6.5%, signals dovish stance on inflation"
result = analyzer.analyze(text)
print(result)

# Expected output format:
# Sentiment: Bullish (75% confidence)
# Key factors: Rate stability, dovish stance
# Impact: Positive for Nifty, especially financials
# Trading implications: Consider bullish strategies
```

## Use Cases
- Pre-market sentiment analysis
- News-driven trading decisions
- Risk assessment based on market mood
- Strategy adjustment based on sentiment shifts
