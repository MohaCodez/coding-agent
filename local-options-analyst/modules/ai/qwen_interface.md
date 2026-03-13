# qwen_interface.py

## Purpose
Provides interface to interact with locally running Ollama Qwen 3B model for AI-powered analysis.

## Inputs
- `model`: Model name (default: "qwen2.5:3b")
- `base_url`: Ollama API endpoint (default: "http://localhost:11434")
- `prompt`: Text prompt for generation
- `temperature`: Randomness (0.0-1.0, default: 0.7)
- `max_tokens`: Maximum response length (default: 2000)

## Outputs
- String response from Qwen model
- Error message if request fails

## Usage Examples

```python
from modules.ai.qwen_interface import QwenInterface

# Initialize
qwen = QwenInterface()

# Generate response
prompt = "Analyze this portfolio: NIFTY 21000 CE Long x50"
response = qwen.generate(prompt, temperature=0.7)
print(response)

# Custom model
qwen_custom = QwenInterface(model="qwen2.5:7b")
```

## Use Cases in Project
1. **Portfolio Analysis**: Analyze positions, risk exposure, allocation
2. **Options Strategy**: Suggest strategies based on market view
3. **Sentiment Analysis**: Interpret market news and sentiment
