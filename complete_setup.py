#!/usr/bin/env python3
"""Complete the assistant project setup"""

import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"✓ {path}")

print("Creating remaining project files...\n")

# Index modules
create_file("assistant/index/symbol_index.py", '''import ast
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
''')

create_file("assistant/index/semantic_index.py", '''import os
import requests
import math
import json
import hashlib

class SemanticIndex:
    def __init__(self, ollama_url="http://localhost:11434", model="nomic-embed-text", cache_dir=None):
        self.documents = []
        self.embeddings = []
        self.ollama_url = ollama_url
        self.model = model
        self.cache_dir = cache_dir or ".assistant/cache"
        self.cache_file = os.path.join(self.cache_dir, "semantic_index.json")
        self.max_chunks = 2000
    
    def _compute_repo_hash(self, repo_path="."):
        hasher = hashlib.sha256()
        skip_dirs = {"__pycache__", ".venv", ".git", "node_modules", "venv", ".tox"}
        files = []
        for root, dirs, filenames in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for f in filenames:
                if f.endswith(".py"):
                    files.append(os.path.join(root, f))
        files.sort()
        for file_path in files:
            try:
                mtime = os.path.getmtime(file_path)
                hasher.update(f"{file_path}:{mtime}".encode())
            except:
                pass
        return hasher.hexdigest()
    
    def _load_cache(self):
        if not os.path.exists(self.cache_file):
            return False
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            if cache.get("repo_hash") == self._compute_repo_hash():
                self.documents = cache["documents"]
                self.embeddings = cache["embeddings"]
                return True
        except:
            pass
        return False
    
    def _save_cache(self, repo_path="."):
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            cache = {"repo_hash": self._compute_repo_hash(repo_path), "documents": self.documents, "embeddings": self.embeddings}
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f)
        except:
            pass
    
    def build(self, repo_path=".", chunk_lines=100, force=False):
        if not force and self._load_cache():
            return len(self.documents)
        self.documents = []
        self.embeddings = []
        skip_dirs = {"__pycache__", ".venv", ".git", "node_modules", "venv", ".tox"}
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for file in files:
                if file.endswith(".py"):
                    self._index_file(os.path.join(root, file), chunk_lines)
                    if len(self.documents) >= self.max_chunks:
                        break
            if len(self.documents) >= self.max_chunks:
                break
        self._save_cache(repo_path)
        return len(self.documents)
    
    def _index_file(self, file_path, chunk_lines):
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            for i in range(0, len(lines), chunk_lines):
                chunk = "".join(lines[i:i + chunk_lines])
                if len(chunk.strip()) < 50:
                    continue
                embedding = self._get_embedding(chunk)
                if embedding:
                    self.documents.append({"file": file_path, "content": chunk[:500]})
                    self.embeddings.append(embedding)
        except:
            pass
    
    def _get_embedding(self, text):
        try:
            response = requests.post(f"{self.ollama_url}/api/embeddings", json={"model": self.model, "prompt": text}, timeout=30)
            response.raise_for_status()
            return response.json()["embedding"]
        except:
            return None
    
    def _cosine_similarity(self, vec1, vec2):
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)
    
    def search(self, query, top_k=5):
        if not self.embeddings:
            return []
        query_embedding = self._get_embedding(query)
        if not query_embedding:
            return []
        scores = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            scores.append((i, similarity))
        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in scores[:top_k]:
            results.append({"file": self.documents[idx]["file"], "score": round(score, 3), "content": self.documents[idx]["content"]})
        return results
''')

create_file("assistant/tools/find_symbol.py", '''from assistant.index.symbol_index import get_shared_index

class FindSymbolTool:
    name = "find_symbol"
    description = "Find function, class, or method definitions by name"
    arguments = {
        "type": "object",
        "properties": {"name": {"type": "string", "description": "Symbol name to search"}},
        "required": ["name"]
    }
    
    def run(self, args):
        try:
            index = get_shared_index()
            matches = index.find_symbol(args["name"])
            if not matches:
                return {"success": True, "output": f"No symbols found matching '{args['name']}'", "metadata": {"count": 0}}
            lines = [f"Found {len(matches)} symbol(s):\\n"]
            for match in matches[:20]:
                lines.append(f"{match['name']} ({match['type']})")
                lines.append(f"  {match['file']}:{match['line']}\\n")
            return {"success": True, "output": "\\n".join(lines), "metadata": {"count": len(matches)}}
        except Exception as e:
            return {"success": False, "error": str(e), "output": "", "metadata": {}}
''')

create_file("assistant/tools/find_callers.py", '''from assistant.index.symbol_index import get_shared_index

class FindCallersTool:
    name = "find_callers"
    description = "Find all functions that call a specific function"
    arguments = {
        "type": "object",
        "properties": {"name": {"type": "string", "description": "Function name to find callers for"}},
        "required": ["name"]
    }
    
    def run(self, args):
        try:
            index = get_shared_index()
            matches = index.find_callers(args["name"])
            if not matches:
                return {"success": True, "output": f"No callers found for '{args['name']}'", "metadata": {"count": 0}}
            lines = [f"Found {len(matches)} caller(s) of {args['name']}:\\n"]
            for match in matches[:20]:
                lines.append(f"{match['caller']}")
                lines.append(f"  {match['file']}:{match['line']}\\n")
            return {"success": True, "output": "\\n".join(lines), "metadata": {"count": len(matches)}}
        except Exception as e:
            return {"success": False, "error": str(e), "output": "", "metadata": {}}
''')

create_file("assistant/tools/semantic_search.py", '''from assistant.index.semantic_index import SemanticIndex

class SemanticSearchTool:
    name = "semantic_search"
    description = "Search code semantically using natural language queries"
    arguments = {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "Natural language description"}},
        "required": ["query"]
    }
    
    def __init__(self):
        self.index = None
    
    def _ensure_index(self):
        if self.index is None:
            self.index = SemanticIndex()
            count = self.index.build()
            if count == 0:
                raise Exception("No documents indexed")
    
    def run(self, args):
        try:
            self._ensure_index()
            results = self.index.search(args["query"], top_k=5)
            if not results:
                return {"success": True, "output": f"No semantic matches found for '{args['query']}'", "metadata": {"count": 0}}
            lines = [f"Top semantic matches for '{args['query']}':\\n"]
            for result in results:
                lines.append(f"{result['file']} (score: {result['score']})")
                lines.append(f"{result['content'][:300]}...")
                lines.append("")
            return {"success": True, "output": "\\n".join(lines), "metadata": {"count": len(results)}}
        except Exception as e:
            return {"success": False, "error": str(e), "output": "", "metadata": {}}
''')

create_file("assistant/tools/registry.py", '''from .search_repo import SearchRepoTool
from .read_file import ReadFileTool
from .write_file import WriteFileTool
from .shell import ShellTool
from .git_tool import GitTool
from .list_files import ListFilesTool
from .apply_patch import ApplyPatchTool
from .find_symbol import FindSymbolTool
from .find_callers import FindCallersTool
from .semantic_search import SemanticSearchTool
from .edit_symbol import EditSymbolTool
from .generate_test import GenerateTestTool
from .git_diff import GitDiffTool

TOOLS = {
    "search_repo": SearchRepoTool(),
    "read_file": ReadFileTool(),
    "write_file": WriteFileTool(),
    "shell": ShellTool(),
    "git": GitTool(),
    "list_files": ListFilesTool(),
    "apply_patch": ApplyPatchTool(),
    "find_symbol": FindSymbolTool(),
    "find_callers": FindCallersTool(),
    "semantic_search": SemanticSearchTool(),
    "edit_symbol": EditSymbolTool(),
    "generate_test": GenerateTestTool(),
    "git_diff": GitDiffTool()
}

def get_tool(name):
    return TOOLS.get(name)

def get_tool_descriptions():
    return [{"name": tool.name, "description": tool.description, "arguments": tool.arguments} for tool in TOOLS.values()]
''')

print("\n✓ All tool files created!")
print("\nNext: Run 'python3 create_agent_files.py'")
