from assistant.index.symbol_index import get_shared_index

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
            lines = [f"Found {len(matches)} caller(s) of {args['name']}:\n"]
            for match in matches[:20]:
                lines.append(f"{match['caller']}")
                lines.append(f"  {match['file']}:{match['line']}\n")
            return {"success": True, "output": "\n".join(lines), "metadata": {"count": len(matches)}}
        except Exception as e:
            return {"success": False, "error": str(e), "output": "", "metadata": {}}
