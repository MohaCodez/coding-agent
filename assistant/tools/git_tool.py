import subprocess

class GitTool:
    name = "git"
    description = "Execute git commands"
    arguments = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Git subcommand (e.g., 'status', 'log')"}
        },
        "required": ["command"]
    }
    
    def run(self, args):
        command = args["command"]
        
        try:
            result = subprocess.run(
                f"git {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout + result.stderr,
                "metadata": {"returncode": result.returncode}
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": "",
                "metadata": {}
            }
