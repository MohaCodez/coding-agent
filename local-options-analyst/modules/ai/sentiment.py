from modules.ai.qwen_interface import QwenInterface
from utils.file_io import read_prompt
import json

class SentimentAnalyzer:
    def __init__(self):
        self.qwen = QwenInterface()
    
    def analyze(self, text):
        """Analyze sentiment with structured JSON output."""
        prompt_template = read_prompt('sentiment_prompt')
        prompt = prompt_template.format(text=text)
        response = self.qwen.generate(prompt, temperature=0.3)
        return self._parse_sentiment_json(response)
    
    def analyze_text(self, text):
        """Analyze sentiment and return text format (legacy)."""
        result = self.analyze(text)
        return self._format_sentiment_text(result)
    
    def analyze_json(self, text, underlying="NIFTY"):
        """Analyze sentiment and return structured JSON with score -1 to 1."""
        result = self.analyze(text)
        
        # Extract specific underlying if requested
        if underlying in result.get("underlying_sentiment", {}):
            return {
                "sentiment_score": result["underlying_sentiment"][underlying]["score"],
                "confidence": result["underlying_sentiment"][underlying]["confidence"],
                "classification": result["overall_sentiment"]["classification"],
                "impact": result["underlying_sentiment"][underlying]["impact"],
                "key_factors": result.get("key_factors", [])
            }
        
        # Return overall sentiment
        return {
            "sentiment_score": result["overall_sentiment"]["score"],
            "confidence": result["overall_sentiment"]["confidence"],
            "classification": result["overall_sentiment"]["classification"],
            "key_factors": result.get("key_factors", [])
        }
    
    def _parse_sentiment_json(self, response):
        """Extract and parse JSON from AI response."""
        try:
            # Remove markdown code blocks if present
            response = response.replace('```json', '').replace('```', '')
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            pass
        
        # Return fallback structure
        return {
            "overall_sentiment": {
                "classification": "neutral",
                "score": 0.0,
                "confidence": 0.5
            },
            "underlying_sentiment": {
                "NIFTY": {"score": 0.0, "impact": "Unable to parse", "confidence": 0.5}
            },
            "key_factors": ["Unable to parse response"],
            "trading_implications": {
                "recommended_bias": "neutral",
                "strategies": [],
                "risk_factors": []
            },
            "error": "Failed to parse JSON response"
        }
    
    def _format_sentiment_text(self, sentiment_data):
        """Format sentiment JSON as readable text."""
        overall = sentiment_data["overall_sentiment"]
        text = f"Sentiment: {overall['classification'].upper()} (Score: {overall['score']:.2f}, Confidence: {overall['confidence']:.0%})\n\n"
        
        text += "Key Factors:\n"
        for factor in sentiment_data.get("key_factors", []):
            text += f"  • {factor}\n"
        
        text += "\nUnderlying Impact:\n"
        for symbol, data in sentiment_data.get("underlying_sentiment", {}).items():
            text += f"  {symbol}: {data['score']:+.2f} - {data['impact']}\n"
        
        text += "\nTrading Implications:\n"
        implications = sentiment_data.get("trading_implications", {})
        text += f"  Bias: {implications.get('recommended_bias', 'N/A')}\n"
        for strategy in implications.get("strategies", []):
            text += f"  • {strategy}\n"
        
        return text
