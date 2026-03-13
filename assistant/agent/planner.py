import json
import re

def parse_llm_response(content):
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    match = re.search(r'(?:json)?\s*(\{.*?\})\s*', content, re.DOTALL)
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
