import subprocess
import os

class SearchRepoTool:
    name = "search_repo"
    description = "Search for text patterns in repository using ripgrep"
    arguments = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search pattern"},
            "file_pattern": {"type": "string", "description": "File pattern (e.g., '*.py')"}
        },
        "required": ["query"]
    }
    
    def run(self, args):
        query = args["query"]
        file_pattern = args.get("file_pattern", "")
        
        cmd = ["rg", "-n", "--max-count", "10", query]
        if file_pattern:
            cmd.extend(["-g", file_pattern])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return {
                "success": True,
                "output": result.stdout if result.stdout else "No matches found",
                "metadata": {"matches": len(result.stdout.splitlines())}
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": "",
                "metadata": {}
            }
