from assistant.index.symbol_index import get_shared_index

class FindSymbolTool:
    name = "find_symbol"
    description = "Find function, class, or method definitions by name"
    arguments = {
        "type": "object",
        "properties": {"name": {"type": "string", "description": "Symbol name to search"}},
        "required": ["name"]
    }
    
    def run(self, args):
        try:
            index = get_shared_index()
            matches = index.find_symbol(args["name"])
            if not matches:
                return {"success": True, "output": f"No symbols found matching '{args['name']}'", "metadata": {"count": 0}}
            lines = [f"Found {len(matches)} symbol(s):\n"]
            for match in matches[:20]:
                lines.append(f"{match['name']} ({match['type']})")
                lines.append(f"  {match['file']}:{match['line']}\n")
            return {"success": True, "output": "\n".join(lines), "metadata": {"count": len(matches)}}
        except Exception as e:
            return {"success": False, "error": str(e), "output": "", "metadata": {}}
