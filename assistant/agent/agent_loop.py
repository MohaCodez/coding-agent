from assistant.llm.ollama_client import OllamaClient
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
    return output[:max_len] + f"\n... (truncated, {len(output) - max_len} chars omitted)"

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
            print(f"\n{'='*60}")
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
                print(f"Context built: {len(repo_context)} chars\n")
    plan = None
    # Only plan for complex queries mentioning code elements
    if len(instruction.split()) > 5 and any(word in instruction.lower() for word in ['file', 'function', 'class', 'refactor', 'modify', 'change', 'update']):
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
            print(f"\n{'='*60}")
            print(f"Iteration {iteration + 1}")
            print('='*60)
        history = trim_history(history)
        current_messages = history.copy()
        if plan and len(plan) > len(completed_steps):
            remaining_steps = plan[len(completed_steps):]
            plan_context = "Remaining plan steps:\n" + "\n".join(f"{i}. {s}" for i, s in enumerate(remaining_steps, len(completed_steps) + 1))
            current_messages.append({"role": "system", "content": plan_context})
        try:
            response = client.chat(current_messages, temperature=0.3)
        except Exception as e:
            return f"Error calling LLM: {e}"
        
        # Try to parse as JSON, but fallback to direct answer if it fails repeatedly
        try:
            action_data = parse_llm_response(response)
            validate_action(action_data)
        except Exception as e:
            if debug:
                print(f"\n[Parse Error] {e}")
                print(f"Raw response: {response[:300]}...")
            
            # If this is iteration 2+ and still failing, treat response as direct answer
            if iteration >= 1:
                if debug:
                    print("\n[Fallback] Treating response as direct answer")
                return response.strip()
            
            # Otherwise, give feedback and retry
            history.append({"role": "assistant", "content": response})
            history.append({"role": "user", "content": "Please respond with valid JSON in this format: {\"thought\": \"your reasoning\", \"action\": \"tool_name\", \"args\": {...}} OR {\"thought\": \"your reasoning\", \"final_answer\": \"your answer\"}"})
            continue
        
        thought = action_data.get("thought", "")
        if debug:
            print(f"\nThought: {thought}")
        if "plan" in action_data and not plan:
            plan = action_data["plan"]
            if debug:
                print(f"\nPlan:")
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
                            print(f"\n{'='*60}")
                            print("Git Diff:")
                            print('='*60)
                            print(diff_result["output"][:500])
                        history.append({"role": "system", "content": f"Code changes:\n{diff_result['output']}"})
            # Skip reflection for simple queries
            if reflection_count < MAX_REFLECTION_ATTEMPTS and files_modified:
                approved, feedback = self_reflect(client, history, files_modified, debug)
                reflection_count += 1
                if approved:
                    if debug:
                        print(f"\n{'='*60}")
                        print("Final Answer:")
                        print('='*60)
                        print(pending_final_answer)
                    return pending_final_answer
                else:
                    if debug:
                        print(f"\nReflection feedback: {feedback}")
                        print("Continuing reasoning...")
                    history.append({"role": "assistant", "content": response})
                    history.append({"role": "user", "content": f"Reflection feedback: {feedback}. Please address these concerns."})
                    continue
            else:
                if debug:
                    print(f"\n{'='*60}")
                    print("Final Answer:")
                    print('='*60)
                    print(pending_final_answer)
                return pending_final_answer
        action_name = action_data["action"]
        args = action_data["args"]
        if debug:
            print(f"\nAction: {action_name}")
            print(f"Args: {json.dumps(args, indent=2)}")
        tool = get_tool(action_name)
        if not tool:
            error_result = {"success": False, "error": f"Unknown tool: {action_name}. Available: {', '.join([t['name'] for t in tools])}", "output": "", "metadata": {}}
            history.append({"role": "assistant", "content": response})
            history.append({"role": "tool", "name": action_name, "content": json.dumps(error_result)})
            if debug:
                print(f"\n[Tool Error] {error_result['error']}")
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
            print(f"\nTool Result:")
            print(f"  Success: {result.get('success', False)}")
            if result.get('error'):
                print(f"  Error: {result['error']}")
            output_preview = result.get('output', '')[:200]
            print(f"  Output: {output_preview}{'...' if len(result.get('output', '')) > 200 else ''}")
        history.append({"role": "assistant", "content": response})
        history.append({"role": "tool", "name": action_name, "content": json.dumps(result)})
    return f"Max iterations ({max_iterations}) reached without completion"
