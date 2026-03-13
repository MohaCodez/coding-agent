import subprocess

class GitDiffTool:
    name = "git_diff"
    description = "Show git diff of uncommitted changes to review code modifications"
    arguments = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Optional: specific file to diff"}
        }
    }
    MAX_OUTPUT = 3000
    
    def run(self, args):
        file_path = args.get("file_path", "")
        cmd = ["git", "diff"]
        if file_path:
            cmd.append(file_path)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = result.stdout
            if len(output) > self.MAX_OUTPUT:
                output = output[:self.MAX_OUTPUT] + f"\n... (truncated, {len(result.stdout) - self.MAX_OUTPUT} chars omitted)"
            if not output:
                output = "No changes detected"
            return {"success": True, "output": output, "metadata": {"has_changes": bool(result.stdout), "truncated": len(result.stdout) > self.MAX_OUTPUT}}
        except Exception as e:
            return {"success": False, "error": str(e), "output": "", "metadata": {}}
