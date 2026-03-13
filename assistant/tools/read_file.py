import os

class ReadFileTool:
    name = "read_file"
    description = "Read contents of a file"
    arguments = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path relative to repo root"},
            "max_lines": {"type": "integer", "description": "Maximum lines to read (default 200)"}
        },
        "required": ["path"]
    }
    
    MAX_FILE_SIZE = 200*1024  # 200KB
    
    def run(self, args):
        path = args["path"]
        maxlines = args.get("max_lines", 200)
        
        if not os.path.exists(path):
            return {
                "success": False,
                "error": f"File not found: {path}",
                "output": "",
                "metadata": {}
            }
        
        try:
            file_size = os.path.getsize(path)
            if file_size > self.MAX_FILE_SIZE:
                return {
                    "success": False,
                    "error": f"File too large: {file_size} bytes (max {self.MAX_FILE_SIZE})",
                    "output": "",
                    "metadata": {"file_size": file_size}
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Cannot access file: {e}",
                "output": "",
                "metadata": {}
            }
        
        try:
            with open(path, 'r') as f:
                lines = f.readlines()[:maxlines]
            
            truncated = len(lines) >= maxlines
            return {
                "success": True,
                "output": "".join(lines),
                "metadata": {"lines": len(lines), "truncated": truncated}
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": "",
                "metadata": {}
            }
