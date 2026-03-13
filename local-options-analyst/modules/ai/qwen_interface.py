import requests
import json

class QwenInterface:
    def __init__(self, model="qwen2.5-coder:3b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def generate(self, prompt, temperature=0.7, max_tokens=2000):
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f"Error: {str(e)}"
