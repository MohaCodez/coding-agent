import json
import os
from datetime import datetime

class AgentMemory:
    def __init__(self, memory_dir=None):
        self.memory_dir = memory_dir or ".assistant/memory"
        self.memory_file = os.path.join(self.memory_dir, "history.json")
        self.max_entries = 50
    
    def _ensure_dir(self):
        try:
            os.makedirs(self.memory_dir, exist_ok=True)
        except:
            pass
    
    def _load_history(self):
        if not os.path.exists(self.memory_file):
            return []
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_history(self, history):
        try:
            self._ensure_dir()
            with open(self.memory_file, 'w') as f:
                json.dump(history[-self.max_entries:], f, indent=2)
        except:
            pass
    
    def add_entry(self, instruction, summary, files_modified=None):
        history = self._load_history()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "instruction": instruction[:200],
            "summary": summary,
            "files_modified": files_modified or []
        }
        history.append(entry)
        self._save_history(history)
    
    def get_recent(self, count=5):
        history = self._load_history()
        return history[-count:] if history else []
    
    def format_context(self, count=5):
        recent = self.get_recent(count)
        if not recent:
            return ""
        lines = ["Recent assistant activity:\n"]
        for entry in recent:
            lines.append(f"- {entry['summary']}")
        return "\n".join(lines)
