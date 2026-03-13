import requests
import json
import sys

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5-coder:1.5b"):
        self.base_url = base_url
        self.model = model
    
    def chat(self, messages, temperature=0.7, stream=False):
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature
        }
        
        try:
            if stream:
                response = requests.post(url, json=payload, timeout=120, stream=True)
                response.raise_for_status()
                full_content = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            content = chunk["message"]["content"]
                            full_content += content
                            print(content, end="", flush=True)
                print()  # newline at end
                return full_content
            else:
                response = requests.post(url, json=payload, timeout=120)
                response.raise_for_status()
                return response.json()["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {e}")
    
    def parse_json_response(self, content):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            if "json" in content:
                start = content.find("json") + 7
                end = content.find("", start)
                content = content[start:end].strip()
            return json.loads(content)

