#!/usr/bin/env python3
"""
Script to create remaining project files
Run this after the bash script completes
"""

import os

# File contents dictionary
files = {
   "assistant/tools/apply_patch.py": '''import os
import re

class ApplyPatchTool:
   name = "apply_patch"
   description = "Apply a unified diff patch to modify specific lines in a file"
   arguments = {
       "type": "object",
       "properties": {
           "patch": {"type": "string", "description": "Unified diff patch"}
       },
       "required": ["patch"]
   }
   
   MAX_MODIFICATION_RATIO = 0.3
   
   def parse_patch(self, patch):
       lines = patch.strip().split('\\n')
       file_path = None
       for line in lines:
           if line.startswith('---'):
               file_path = line.split()[1]
           elif line.startswith('+++'):
               file_path = line.split()[1]
               break
       
       if not file_path:
           raise ValueError("Cannot extract file path from patch")
       
       hunks = []
       current_hunk = None
       
       for line in lines:
           if line.startswith('@@'):
               match = re.search(r'@@ -(\\d+),?(\\d*) \\+(\\d+),?(\\d*) @@', line)
               if match:
                   old_start = int(match.group(1))
                   current_hunk = {'old_start': old_start, 'changes': []}
                   hunks.append(current_hunk)
           elif current_hunk is not None:
               if line.startswith('-'):
                   current_hunk['changes'].append(('remove', line[1:]))
               elif line.startswith('+'):
                   current_hunk['changes'].append(('add', line[1:]))
               elif line.startswith(' '):
                   current_hunk['changes'].append(('context', line[1:]))
       
       return file_path, hunks
   
   def validate_context(self, file_lines, start_index, changes):
       file_idx = start_index
       for change_type, content in changes:
           if change_type == 'context':
               if file_idx >= len(file_lines):
                   return False, f"Context line beyond file end at line {file_idx + 1}"
               if file_lines[file_idx].rstrip() != content.rstrip():
                   return False, f"Context mismatch at line {file_idx + 1}"
               file_idx += 1
           elif change_type == 'remove':
               if file_idx >= len(file_lines):
                   return False, f"Remove line beyond file end at line {file_idx + 1}"
               file_idx += 1
       return True, None
   
   def validate_path_security(self, file_path):
       abs_path = os.path.abspath(file_path)
       repo_root = os.path.abspath(os.getcwd())
       if not abs_path.startswith(repo_root):
           return False, "Patch attempts to modify file outside project directory"
       return True, None
   
   def apply_hunks(self, file_lines, hunks):
       result = file_lines[:]
       offset = 0
       for hunk in hunks:
           line_idx = hunk['old_start'] - 1 + offset
           changes = hunk['changes']
           removes = []
           adds = []
           for change_type, content in changes:
               if change_type == 'remove':
                   removes.append(content)
               elif change_type == 'add':
                   adds.append(content + '\\n')
           for  in removes:
               if lineidx < len(result):
                   result.pop(line_idx)
                   offset -= 1
           for add_line in adds:
               result.insert(line_idx, add_line)
               line_idx += 1
               offset += 1
       return result
   
   def run(self, args):
       patch = args["patch"]
       if "\\x00" in patch:
           return {"success": False, "error": "Binary content detected in patch", "output": "", "metadata": {}}
       try:
           file_path, hunks = self.parse_patch(patch)
       except Exception as e:
           return {"success": False, "error": f"Failed to parse patch: {e}", "output": "", "metadata": {}}
       valid, error = self.validate_path_security(file_path)
       if not valid:
           return {"success": False, "error": error, "output": "", "metadata": {}}
       if not os.path.exists(file_path):
           return {"success": False, "error": f"File not found: {file_path}", "output": "", "metadata": {}}
       try:
           with open(file_path, 'r') as f:
               file_lines = f.readlines()
       except Exception as e:
           return {"success": False, "error": f"Cannot read file: {e}", "output": "", "metadata": {}}
       for hunk in hunks:
           valid, error = self.validate_context(file_lines, hunk['old_start'] - 1, hunk['changes'])
           if not valid:
               return {"success": False, "error": f"Patch context mismatch: {error}", "output": "", "metadata": {}}
       total_changes = sum(len([c for c in hunk['changes'] if c[0] in ('add', 'remove')]) for hunk in hunks)
       if total_changes > len(file_lines)  self.MAXMODIFICATION_RATIO:
           return {"success": False, "error": f"Patch modifies too many lines ({total_changes} changes, max {int(len(file_lines)  self.MAXMODIFICATION_RATIO)})", "output": "", "metadata": {}}
       try:
           modified_lines = self.apply_hunks(file_lines, hunks)
       except Exception as e:
           return {"success": False, "error": f"Failed to apply patch: {e}", "output": "", "metadata": {}}
       try:
           with open(file_path, 'w') as f:
               f.writelines(modified_lines)
       except Exception as e:
           return {"success": False, "error": f"Failed to write file: {e}", "output": "", "metadata": {}}
       return {"success": True, "output": f"Patch applied to {file_path}: {total_changes} changes", "metadata": {"file": file_path, "changes": total_changes, "hunks": len(hunks)}}
''',

   "assistant/tools/edit_symbol.py": '''import ast
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
                   new_lines.append(' '  indent + line + '\\n')
               else:
                   newlines.append('\\n')
           updated_lines = lines[:start_line] + new_lines + lines[end_line:]
           with open(file_path, 'w') as f:
               f.writelines(updated_lines)
           return {"success": True, "output": f"Edited {symbol_name} in {file_path}", "metadata": {"file": file_path, "symbol": symbol_name, "lines_replaced": end_line - start_line}}
       except SyntaxError as e:
           return {"success": False, "error": f"Syntax error in file: {e}", "output": "", "metadata": {}}
       except Exception as e:
           return {"success": False, "error": str(e), "output": "", "metadata": {}}
''',

   "assistant/tools/generate_test.py": '''import ast
import os
from assistant.llm.ollama_client import OllamaClient

class GenerateTestTool:
   name = "generate_test"
   description = "Generate a pytest-style unit test for a function or class"
   arguments = {
       "type": "object",
       "properties": {
           "file_path": {"type": "string", "description": "Path to Python file"},
           "symbol_name": {"type": "string", "description": "Function or class name to test"}
       },
       "required": ["file_path", "symbol_name"]
   }
   
   def run(self, args):
       file_path = args["file_path"]
       symbol_name = args["symbol_name"]
       if not os.path.exists(file_path):
           return {"success": False, "error": f"File not found: {file_path}", "output": "", "metadata": {}}
       try:
           with open(file_path, 'r') as f:
               content = f.read()
           tree = ast.parse(content, filename=file_path)
           target_code = None
           for node in ast.walk(tree):
               if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                   if node.name == symbol_name:
                       lines = content.splitlines()
                       start = node.lineno - 1
                       end = node.end_lineno
                       target_code = "\\n".join(lines[start:end])
                       break
           if not target_code:
               return {"success": False, "error": f"Symbol '{symbol_name}' not found in {file_path}", "output": "", "metadata": {}}
           prompt = f"""Write a simple pytest test for this function. Respond only with Python test code.

{target_code}

Test function name should be: test_{symbol_name}"""
           client = OllamaClient()
           test_code = client.chat([{"role": "user", "content": prompt}], temperature=0.3)
           if "python" in test_code:
                test_code = test_code.split("python")[1].split("")[0].strip()
            elif "" in test_code:
               test_code = test_code.split("")[1].split("")[0].strip()
           return {"success": True, "output": test_code, "metadata": {"file": file_path, "symbol": symbol_name}}
       except Exception as e:
           return {"success": False, "error": str(e), "output": "", "metadata": {}}
''',

   "assistant/tools/git_diff.py": '''import subprocess

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
               output = output[:self.MAX_OUTPUT] + f"\\n... (truncated, {len(result.stdout) - self.MAX_OUTPUT} chars omitted)"
           if not output:
               output = "No changes detected"
           return {"success": True, "output": output, "metadata": {"has_changes": bool(result.stdout), "truncated": len(result.stdout) > self.MAX_OUTPUT}}
       except Exception as e:
           return {"success": False, "error": str(e), "output": "", "metadata": {}}
''',
}

# Create files
for filepath, content in files.items():
   os.makedirs(os.path.dirname(filepath), exist_ok=True)
   with open(filepath, 'w') as f:
       f.write(content)
   print(f"Created: {filepath}")

print("\nRemaining files created successfully!")
print("Run the main setup script to continue...")
