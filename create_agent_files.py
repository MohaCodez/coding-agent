#!/usr/bin/env python3
"""Create agent, context, and CLI files"""

import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"✓ {path}")

print("Creating agent and context files...\n")

create_file("assistant/agent/memory.py", '''import json
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
        lines = ["Recent assistant activity:\\n"]
        for entry in recent:
            lines.append(f"- {entry['summary']}")
        return "\\n".join(lines)
''')

create_file("assistant/agent/planner.py", '''import json
import re

def parse_llm_response(content):
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    match = re.search(r'(?:json)?\\s*(\\{.*?\\})\\s*
', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    first_brace = content.find('{')
    last_brace = content.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(content[first_brace:last_brace + 1])
        except json.JSONDecodeError:
            pass
    raise ValueError("Could not parse JSON from response")

def validate_action(action_data):
    if "final_answer" in action_data:
        return True
    if "plan" in action_data:
        return True
    if "action" not in action_data:
        raise ValueError("Response must contain 'action', 'plan', or 'final_answer'")
    if "args" not in action_data:
        raise ValueError("Action must contain 'args'")
    return True

def create_plan(client, instruction, tools):
    planning_prompt = f"""Given this task: "{instruction}"

Create a short execution plan (3-6 steps) using these available tools:
{', '.join([t['name'] for t in tools])}

Respond with JSON:
{{
  "plan": ["step 1", "step 2", "step 3"]
}}"""
    try:
        response = client.chat([{"role": "user", "content": planning_prompt}], temperature=0.3)
        plan_data = parse_llm_response(response)
        if "plan" in plan_data and isinstance(plan_data["plan"], list):
            return plan_data["plan"]
    except:
        pass
    return None
''')

create_file("assistant/context/file_ranker.py", '''import re

def rank_files(instruction, search_output, max_files=10):
    if not search_output:
        return []
    keywords = set(re.findall(r'\\b\\w{4,}\\b', instruction.lower()))
    file_scores = {}
    lines = search_output.strip().split('\\n')
    for line in lines:
        if not line:
            continue
        match = re.match(r'^([^:]+):\\d+:', line)
        if match:
            file_path = match.group(1)
            file_scores[file_path] = file_scores.get(file_path, 0) + 10
    for file_path in list(file_scores.keys()):
        path_lower = file_path.lower()
        for keyword in keywords:
            if keyword in path_lower:
                file_scores[file_path] += 5
    ranked = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)
    return [path for path, score in ranked[:max_files]]
''')

create_file("assistant/context/repo_context.py", '''import re
from assistant.tools.registry import get_tool
from assistant.context.file_ranker import rank_files

def build_repo_context(query, max_chars_per_file=1200):
    search_tool = get_tool("search_repo")
    read_tool = get_tool("read_file")
    search_result = search_tool.run({"query": query})
    if not search_result["success"] or not search_result["output"]:
        return ""
    ranked_files = rank_files(query, search_result["output"], max_files=3)
    if not ranked_files:
        return ""
    context_parts = ["Repository Context (relevant files):\\n"]
    for path in ranked_files:
        read_result = read_tool.run({"path": path, "max_lines": 40})
        if read_result["success"]:
            content = read_result["output"][:max_chars_per_file]
            context_parts.append(f"\\nFile: {path}")
            context_parts.append(content)
            context_parts.append("---")
    return "\\n".join(context_parts)
''')

create_file("assistant/context/repo_map.py", '''from assistant.index.symbol_index import get_shared_index
from collections import defaultdict

def generate_repo_map(max_lines=200):
    try:
        index = get_shared_index()
        symbols = index.list_symbols()
        if not symbols:
            return ""
        file_symbols = defaultdict(list)
        for symbol in symbols:
            file_symbols[symbol['file']].append(symbol)
        lines = ["Repository Structure Map:\\n"]
        line_count = 0
        for file_path in sorted(file_symbols.keys()):
            if line_count >= max_lines:
                break
            lines.append(f"\\n{file_path}")
            line_count += 1
            for symbol in sorted(file_symbols[file_path], key=lambda s: s['line']):
                if line_count >= max_lines:
                    break
                symbol_type = symbol['type']
                symbol_name = symbol['name']
                if symbol_type == 'class':
                    lines.append(f"  class {symbol_name}")
                elif symbol_type == 'function':
                    lines.append(f"  def {symbol_name}()")
                elif symbol_type == 'method':
                    lines.append(f"    {symbol_name.split('.')[-1]}()")
                line_count += 1
        return "\\n".join(lines)
    except:
        return ""
''')

create_file("assistant/agent/agent_loop.py", '''from assistant.llm.ollama_client import OllamaClient
from assistant.tools.registry import get_tool, get_tool_descriptions
from assistant.config.prompts import build_system_prompt
from assistant.agent.planner import parse_llm_response, validate_action, create_plan
from assistant.context.repo_context import build_repo_context
from assistant.context.repo_map import generate_repo_map
from assistant.agent.memory import AgentMemory
import json

MAX_TOOL_OUTPUT = 2000
MAX_REFLECTION_ATTEMPTS = 2

def trim_history(history):
    system_messages = [msg for msg in history if msg["role"] == "system"]
    other_messages = [msg for msg in history if msg["role"] != "system"]
    if len(other_messages) <= 10:
        return history
    return system_messages + other_messages[-10:]

def truncate_output(output, max_len=MAX_TOOL_OUTPUT):
    if len(output) <= max_len:
        return output
    return output[:max_len] + f"\\n... (truncated, {len(output) - max_len} chars omitted)"

def self_reflect(client, history, files_modified, debug=False):
    reflection_prompt = """Review your work and answer:
1. Did all tools execute successfully?
2. If you modified code, was it done safely?
3. Is your answer complete and accurate?

Respond with JSON:
{
  "approved": true/false,
  "feedback": "brief explanation"
}"""
    try:
        reflection_messages = history + [{"role": "user", "content": reflection_prompt}]
        response = client.chat(reflection_messages, temperature=0.3)
        reflection = parse_llm_response(response)
        if debug:
            print(f"\\n{'='*60}")
            print("Self-Reflection:")
            print('='*60)
            print(f"Approved: {reflection.get('approved', False)}")
            print(f"Feedback: {reflection.get('feedback', 'N/A')}")
        return reflection.get("approved", False), reflection.get("feedback", "")
    except:
        return True, ""

def run_agent(instruction, debug=False, max_iterations=20, model=None, use_context=True):
    client = OllamaClient(model=model) if model else OllamaClient()
    tools = get_tool_descriptions()
    system_prompt = build_system_prompt(tools)
    memory = AgentMemory()
    history = [{"role": "system", "content": system_prompt}]
    repo_map = generate_repo_map()
    if repo_map:
        history.append({"role": "system", "content": repo_map})
    memory_context = memory.format_context()
    if memory_context:
        history.append({"role": "system", "content": memory_context})
    if use_context:
        if debug:
            print("Building repository context...")
        repo_context = build_repo_context(instruction)
        if repo_context:
            history.append({"role": "system", "content": repo_context})
            if debug:
                print(f"Context built: {len(repo_context)} chars\\n")
    plan = None
    if len(instruction.split()) > 5:
        if debug:
            print("Generating execution plan...")
        plan = create_plan(client, instruction, tools)
        if plan and debug:
            print("Plan:")
            for i, step in enumerate(plan, 1):
                print(f"  {i}. {step}")
            print()
    history.append({"role": "user", "content": instruction})
    files_modified = []
    completed_steps = []
    reflection_count = 0
    pending_final_answer = None
    for iteration in range(max_iterations):
        if debug:
            print(f"\\n{'='*60}")
            print(f"Iteration {iteration + 1}")
            print('='*60)
        history = trim_history(history)
        current_messages = history.copy()
        if plan and len(plan) > len(completed_steps):
            remaining_steps = plan[len(completed_steps):]
            plan_context = "Remaining plan steps:\\n" + "\\n".join(f"{i}. {s}" for i, s in enumerate(remaining_steps, len(completed_steps) + 1))
            current_messages.append({"role": "system", "content": plan_context})
        try:
            response = client.chat(current_messages, temperature=0.3)
        except Exception as e:
            return f"Error calling LLM: {e}"
        try:
            action_data = parse_llm_response(response)
            validate_action(action_data)
        except Exception as e:
            if debug:
                print(f"\\n[Parse Error] {e}")
                print(f"Raw response: {response[:300]}...")
            history.append({"role": "assistant", "content": response})
            history.append({"role": "user", "content": json.dumps({"success": False, "error": f"Invalid JSON response: {str(e)}", "output": "", "metadata": {}})})
            continue
        thought = action_data.get("thought", "")
        if debug:
            print(f"\\nThought: {thought}")
        if "plan" in action_data and not plan:
            plan = action_data["plan"]
            if debug:
                print(f"\\nPlan:")
                for i, step in enumerate(plan, 1):
                    print(f"  {i}. {step}")
            history.append({"role": "assistant", "content": response})
            history.append({"role": "user", "content": json.dumps({"success": True, "output": "Plan acknowledged. Proceed with execution.", "metadata": {}})})
            continue
        if "final_answer" in action_data:
            pending_final_answer = action_data["final_answer"]
            if files_modified and reflection_count == 0:
                git_diff_tool = get_tool("git_diff")
                if git_diff_tool:
                    diff_result = git_diff_tool.run({})
                    if diff_result.get("success") and diff_result.get("metadata", {}).get("has_changes"):
                        if debug:
                            print(f"\\n{'='*60}")
                            print("Git Diff:")
                            print('='*60)
                            print(diff_result["output"][:500])
                        history.append({"role": "system", "content": f"Code changes:\\n{diff_result['output']}"})
            if reflection_count < MAX_REFLECTION_ATTEMPTS:
                approved, feedback = self_reflect(client, history, files_modified, debug)
                reflection_count += 1
                if approved:
                    if debug:
                        print(f"\\n{'='*60}")
                        print("Final Answer:")
                        print('='*60)
                        print(pending_final_answer)
                    try:
                        summary_prompt = f"Summarize this task in 1-2 sentences: {instruction}"
                        summary = client.chat([{"role": "user", "content": summary_prompt}], temperature=0.3)
                        memory.add_entry(instruction, summary[:200], files_modified)
                    except:
                        pass
                    return pending_final_answer
                else:
                    if debug:
                        print(f"\\nReflection feedback: {feedback}")
                        print("Continuing reasoning...")
                    history.append({"role": "assistant", "content": response})
                    history.append({"role": "user", "content": f"Reflection feedback: {feedback}. Please address these concerns."})
                    continue
            else:
                if debug:
                    print(f"\\n{'='*60}")
                    print("Final Answer (max reflections reached):")
                    print('='*60)
                    print(pending_final_answer)
                try:
                    summary_prompt = f"Summarize this task in 1-2 sentences: {instruction}"
                    summary = client.chat([{"role": "user", "content": summary_prompt}], temperature=0.3)
                    memory.add_entry(instruction, summary[:200], files_modified)
                except:
                    pass
                return pending_final_answer
        action_name = action_data["action"]
        args = action_data["args"]
        if debug:
            print(f"\\nAction: {action_name}")
            print(f"Args: {json.dumps(args, indent=2)}")
        tool = get_tool(action_name)
        if not tool:
            error_result = {"success": False, "error": f"Unknown tool: {action_name}. Available: {', '.join([t['name'] for t in tools])}", "output": "", "metadata": {}}
            history.append({"role": "assistant", "content": response})
            history.append({"role": "tool", "name": action_name, "content": json.dumps(error_result)})
            if debug:
                print(f"\\n[Tool Error] {error_result['error']}")
            continue
        try:
            result = tool.run(args)
            if action_name in ("write_file", "apply_patch", "edit_symbol") and result.get("success"):
                file_path = args.get("path") or args.get("file_path") or result.get("metadata", {}).get("file")
                if file_path and file_path not in files_modified:
                    files_modified.append(file_path)
            if plan and result.get("success"):
                completed_steps.append(action_name)
            if not isinstance(result, dict):
                result = {"success": False, "error": "Tool returned invalid result", "output": "", "metadata": {}}
            if "output" in result and len(result["output"]) > MAX_TOOL_OUTPUT:
                result["output"] = truncate_output(result["output"])
        except Exception as e:
            result = {"success": False, "error": f"Tool execution failed: {str(e)}", "output": "", "metadata": {}}
        if debug:
            print(f"\\nTool Result:")
            print(f"  Success: {result.get('success', False)}")
            if result.get('error'):
                print(f"  Error: {result['error']}")
            output_preview = result.get('output', '')[:200]
            print(f"  Output: {output_preview}{'...' if len(result.get('output', '')) > 200 else ''}")
        history.append({"role": "assistant", "content": response})
        history.append({"role": "tool", "name": action_name, "content": json.dumps(result)})
    return f"Max iterations ({max_iterations}) reached without completion"
''')

print("\n✓ All agent files created!")
print("\nNext: Run 'python3 create_cli.py'")
