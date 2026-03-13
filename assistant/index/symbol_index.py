import ast
import os

_shared_index = None

def get_shared_index():
    global _shared_index
    if _shared_index is None:
        _shared_index = SymbolIndex()
        _shared_index.build()
    return _shared_index

class SymbolIndex:
    def __init__(self):
        self.symbols = []
        self.calls = []
    
    def build(self, repo_path="."):
        self.symbols = []
        self.calls = []
        skip_dirs = {"__pycache__", ".venv", ".git", "node_modules", "venv", ".tox"}
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for file in files:
                if file.endswith(".py"):
                    self._index_file(os.path.join(root, file))
        return len(self.symbols)
    
    def _index_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            tree = ast.parse(content, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.symbols.append({"name": node.name, "type": "function", "file": file_path, "line": node.lineno})
                    self._index_calls(node, node.name, file_path)
                elif isinstance(node, ast.ClassDef):
                    self.symbols.append({"name": node.name, "type": "class", "file": file_path, "line": node.lineno})
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_name = f"{node.name}.{item.name}"
                            self.symbols.append({"name": method_name, "type": "method", "file": file_path, "line": item.lineno})
                            self._index_calls(item, method_name, file_path)
        except:
            pass
    
    def _index_calls(self, func_node, caller_name, file_path):
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                callee = self._extract_call_name(node.func)
                if callee:
                    self.calls.append({"caller": caller_name, "callee": callee, "file": file_path, "line": node.lineno})
    
    def _extract_call_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None
    
    def find_symbol(self, name):
        name_lower = name.lower()
        return [s for s in self.symbols if name_lower in s["name"].lower()]
    
    def find_callers(self, name):
        return [c for c in self.calls if name.lower() in c["callee"].lower()]
    
    def list_symbols(self):
        return self.symbols
    
    def get_stats(self):
        return {"symbols": len(self.symbols), "calls": len(self.calls)}
