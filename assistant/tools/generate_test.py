import ast
import os
from assistant.llm.ollama_client import OllamaClient

class GenerateTestTool:
    name = "generate_test"
    description = "Generate a pytest-style unit test for a function or class"
    arguments = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to Python file"},
            "symbol_name": {"type": "string", "description": "Function or class name to test"}
        },
        "required": ["file_path", "symbol_name"]
    }
    
    def run(self, args):
        file_path = args["file_path"]
        symbol_name = args["symbol_name"]
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}", "output": "", "metadata": {}}
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            tree = ast.parse(content, filename=file_path)
            target_code = None
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if node.name == symbol_name:
                        lines = content.splitlines()
                        start = node.lineno - 1
                        end = node.end_lineno
                        target_code = "\n".join(lines[start:end])
                        break
            if not target_code:
                return {"success": False, "error": f"Symbol '{symbol_name}' not found in {file_path}", "output": "", "metadata": {}}
            prompt = f"""Write a simple pytest test for this function. Respond only with Python test code.

    {target_code}

    Test function name should be: test_{symbol_name}"""
            client = OllamaClient()
            test_code = client.chat([{"role": "user", "content": prompt}], temperature=0.3)
            if "python" in test_code:
                    test_code = test_code.split("python")[1].split("")[0].strip()
            elif "" in test_code:
                test_code = test_code.split("")[1].split("")[0].strip()
            return {"success": True, "output": test_code, "metadata": {"file": file_path, "symbol": symbol_name}}
        except Exception as e:
            return {"success": False, "error": str(e), "output": "", "metadata": {}}
