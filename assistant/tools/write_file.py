import os

class WriteFileTool:
    name = "write_file"
    description = "Write or modify a file"
    arguments = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path"},
            "content": {"type": "string", "description": "File content"}
        },
        "required": ["path", "content"]
    }
    
    def run(self, args):
        path = args["path"]
        content = args["content"]
        
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            return {
                "success": True,
                "output": f"File written: {path}",
                "metadata": {"bytes": len(content)}
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": "",
                "metadata": {}
            }
