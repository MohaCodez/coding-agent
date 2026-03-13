from assistant.index.semantic_index import SemanticIndex

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
            lines = [f"Top semantic matches for '{args['query']}':\n"]
            for result in results:
                lines.append(f"{result['file']} (score: {result['score']})")
                lines.append(f"{result['content'][:300]}...")
                lines.append("")
            return {"success": True, "output": "\n".join(lines), "metadata": {"count": len(results)}}
        except Exception as e:
            return {"success": False, "error": str(e), "output": "", "metadata": {}}
