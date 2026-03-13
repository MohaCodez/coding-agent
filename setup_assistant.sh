#!/bin/bash
# setup_assistant.sh - Creates the complete local AI coding assistant project

set -e

PROJECT_NAME="assistant"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Creating Local AI Coding Assistant..."
echo "======================================"

# Create directory structure
echo "Creating directory structure..."
mkdir -p $PROJECT_NAME/{cli,agent,llm,tools,context,index,config}
mkdir -p docs tests

# Create __init__.py files
touch $PROJECT_NAME/__init__.py
touch $PROJECT_NAME/cli/__init__.py
touch $PROJECT_NAME/agent/__init__.py
touch $PROJECT_NAME/llm/__init__.py
touch $PROJECT_NAME/tools/__init__.py
touch $PROJECT_NAME/context/__init__.py
touch $PROJECT_NAME/index/__init__.py
touch $PROJECT_NAME/config/__init__.py

echo "Creating Python modules..."

# ============================================================================
# LLM Module
# ============================================================================

cat > $PROJECT_NAME/llm/ollama_client.py << 'EOF'
import requests
import json

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="qwen2.5-coder:3b"):
        self.base_url = base_url
        self.model = model
    
    def chat(self, messages, temperature=0.7):
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": temperature
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {e}")
    
    def parse_json_response(self, content):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            if "json" in content:
               start = content.find("json") + 7
                end = content.find("", start)
               content = content[start:end].strip()
           return json.loads(content)
EOF

# ============================================================================
# Config Module
# ============================================================================

cat > $PROJECT_NAME/config/prompts.py << 'EOF'
SYSTEM_PROMPT = """You are a coding assistant that helps developers understand and modify code.

You have access to these tools:
{tools}

Always respond with valid JSON in this format:

For planning (optional):
{{
 "thought": "your reasoning",
 "plan": ["step 1", "step 2", "step 3"]
}}

For tool usage:
{{
 "thought": "your reasoning",
 "action": "tool_name",
 "args": {{"arg1": "value1"}}
}}

When task is complete:
{{
 "thought": "your reasoning",
 "final_answer": "your response to the user"
}}

Rules:
- Use tools to gather information before answering
- Search before reading files
- Read files before modifying them
- Keep responses concise
- Always output valid JSON

Repository Analysis Rules:
- Use find_symbol to locate function/class definitions
- Use find_callers to discover function dependencies
- Use search_repo for exact text/keyword search
- Use semantic_search for conceptual queries (e.g., "authentication logic", "error handling", "database connection")
- Choose the right search tool based on query type

Planning Rules:
- For complex tasks generate a short plan (2-5 steps)
- Plans help organize multi-step workflows
- Follow the plan when using tools

Code Modification Rules:
- When modifying existing code, use apply_patch with unified diff format
- Only use write_file for creating new files
- Never rewrite entire files unless explicitly requested
- Generate minimal patches that change only necessary lines
- Preserve indentation and formatting

Patch format example:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
path/to/file.py
+++ path/to/file.py
@@ -10,3 +10,3 @@
def example():
- print("old")
+    print("new")
"""

def build_system_prompt(tools):
   tool_list = "\n".join([f"- {t['name']}: {t['description']}" for t in tools])
   return SYSTEM_PROMPT.format(tools=tool_list)
EOF

# ============================================================================
# Tools Module - Base Tools
# ============================================================================

cat > $PROJECT_NAME/tools/search_repo.py << 'EOF'
import subprocess
import os

class SearchRepoTool:
   name = "search_repo"
   description = "Search for text patterns in repository using ripgrep"
   arguments = {
       "type": "object",
       "properties": {
           "query": {"type": "string", "description": "Search pattern"},
           "file_pattern": {"type": "string", "description": "File pattern (e.g., '*.py')"}
       },
       "required": ["query"]
   }
   
   def run(self, args):
       query = args["query"]
       file_pattern = args.get("file_pattern", "")
       
       cmd = ["rg", "-n", "--max-count", "10", query]
       if file_pattern:
           cmd.extend(["-g", file_pattern])
       
       try:
           result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
           return {
               "success": True,
               "output": result.stdout if result.stdout else "No matches found",
               "metadata": {"matches": len(result.stdout.splitlines())}
           }
       except Exception as e:
           return {
               "success": False,
               "error": str(e),
               "output": "",
               "metadata": {}
           }
EOF

cat > $PROJECT_NAME/tools/read_file.py << 'EOF'
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
   
   MAX_FILE_SIZE = 200  1024  # 200KB
   
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
               lines = f.readlines()[:max_lines]
           
           truncated = len(lines) >= max_lines
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
EOF

cat > $PROJECT_NAME/tools/write_file.py << 'EOF'
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
EOF

cat > $PROJECT_NAME/tools/shell.py << 'EOF'
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
EOF

cat > $PROJECT_NAME/tools/git_tool.py << 'EOF'
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
EOF

cat > $PROJECT_NAME/tools/list_files.py << 'EOF'
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
EOF

echo "Creating advanced tools (patch, symbol editing, etc.)..."

# Due to length constraints, I'll create a Python script to generate the remaining files

cat > create_remaining_files.py << 'PYTHON_EOF'
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
PYTHON_EOF

chmod +x create_remaining_files.py

echo ""
echo "======================================"
echo "Setup script created!"
echo "======================================"
echo ""
echo "To complete the setup:"
echo "1. Save this script as: setup_assistant.sh"
echo "2. Make it executable: chmod +x setup_assistant.sh"
echo "3. Run it: ./setup_assistant.sh"
echo ""
echo "This will create the basic structure."
echo "Then run: python3 create_remaining_files.py"
echo ""
echo "After that, I'll provide the remaining files in the next message."
echo ""
