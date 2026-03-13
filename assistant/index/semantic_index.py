import os
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
