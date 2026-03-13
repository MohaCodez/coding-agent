import subprocess

class ListFilesTool:
    name = "list_files"
    description = "List files in repository to understand structure"
    arguments = {
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Optional file pattern (e.g., '*.py')"}
        }
    }
    
    def run(self, args):
        pattern = args.get("pattern", "")
        
        cmd = ["rg", "--files", "--hidden", "--glob", "!.git"]
        if pattern:
            cmd.extend(["-g", pattern])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            lines = result.stdout.splitlines()[:200]
            
            return {
                "success": True,
                "output": "\n".join(lines),
                "metadata": {"file_count": len(lines), "truncated": len(result.stdout.splitlines()) > 200}
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": "",
                "metadata": {}
            }
