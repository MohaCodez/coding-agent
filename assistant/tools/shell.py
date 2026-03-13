import subprocess
import os

class ShellTool:
    name = "shell"
    description = "Execute safe shell commands"
    arguments = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Shell command to execute"}
        },
        "required": ["command"]
    }
    
    BLOCKED = ["rm -rf", "sudo", "curl", "wget", "dd", ">", ">>"]
    
    def run(self, args):
        command = args["command"]
        
        if any(blocked in command for blocked in self.BLOCKED):
            return {
                "success": False,
                "error": "Blocked: unsafe command",
                "output": "",
                "metadata": {}
            }
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30,
                cwd=os.getcwd()
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
