import os
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
        lines = patch.strip().split('\n')
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
                match = re.search(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', line)
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
                   adds.append(content + '\n')
           for _ in removes:
               if line_idx < len(result):
                   result.pop(line_idx)
                   offset -= 1
           for add_line in adds:
               result.insert(line_idx, add_line)
               line_idx += 1
               offset += 1
       return result
   
    def run(self, args):
       patch = args["patch"]
       if "\x00" in patch:
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
       if total_changes > len(file_lines) * self.MAXMODIFICATION_RATIO:
           return {"success": False, "error": f"Patch modifies too many lines ({total_changes} changes, max {int(len(file_lines) * self.MAXMODIFICATION_RATIO)})", "output": "", "metadata": {}}
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
