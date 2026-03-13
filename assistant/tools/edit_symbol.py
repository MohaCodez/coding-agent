import ast
import os

class EditSymbolTool:
    name = "edit_symbol"
    description = "Edit a specific function or class by name using AST-aware replacement"
    arguments = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to Python file"},
            "symbol_name": {"type": "string", "description": "Function or class name to edit"},
            "new_code": {"type": "string", "description": "New code for the symbol"}
        },
        "required": ["file_path", "symbol_name", "new_code"]
    }
    
    def run(self, args):
        file_path = args["file_path"]
        symbol_name = args["symbol_name"]
        new_code = args["new_code"]
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}", "output": "", "metadata": {}}
        try:
            with open(file_path, 'r') as f:
                original_content = f.read()
                lines = original_content.splitlines(keepends=True)
            tree = ast.parse(original_content, filename=file_path)
            target_node = None
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if node.name == symbol_name:
                        target_node = node
                        break
            if not target_node:
                return {"success": False, "error": f"Symbol '{symbol_name}' not found in {file_path}", "output": "", "metadata": {}}
            start_line = target_node.lineno - 1
            end_line = target_node.end_lineno
            original_line = lines[start_line]
            indent = len(original_line) - len(original_line.lstrip())
            new_lines = []
            for line in new_code.splitlines():
                if line.strip():
                    new_lines.append(' ',  indent + line + '\n')
                else:
                    new_lines.append('\n')
            updated_lines = lines[:start_line] + new_lines + lines[end_line:]
            with open(file_path, 'w') as f:
                f.writelines(updated_lines)
            return {"success": True, "output": f"Edited {symbol_name} in {file_path}", "metadata": {"file": file_path, "symbol": symbol_name, "lines_replaced": end_line - start_line}}
        except SyntaxError as e:
            return {"success": False, "error": f"Syntax error in file: {e}", "output": "", "metadata": {}}
        except Exception as e:
            return {"success": False, "error": str(e), "output": "", "metadata": {}}
