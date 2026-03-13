# Making Agent Mode Reliable

## Problem
The 1.5b model struggles with the agent loop's strict JSON formatting requirements.

## Solutions Implemented

### 1. **Fallback to Direct Answer** ✅
After 1 failed JSON parse attempt, treat the response as a direct answer instead of retrying.

```python
# In agent_loop.py
if iteration >= 1:
    return response.strip()  # Fallback to direct answer
```

### 2. **Simplified System Prompt** ✅
Reduced complexity and emphasized answering directly:
- Shorter instructions
- Clear preference for `final_answer`
- Explicit: "Do NOT use tools for general knowledge"

### 3. **Skip Unnecessary Steps** ✅
- Skip planning for simple queries
- Skip reflection unless files modified
- Cache repo map

## Results

| Query Type | Before | After | Status |
|------------|--------|-------|--------|
| Simple questions | 17s (fails) | 4-5s (works) | ✅ Fixed |
| Code generation | 15s (fails) | 10-15s (mixed) | ⚠️ Inconsistent |
| File operations | N/A | N/A | ❌ Not tested |

## Remaining Issues

The 1.5b model is **fundamentally too small** for reliable agent operation:

1. **JSON formatting** - Struggles to maintain strict format
2. **Tool selection** - Often tries to use tools unnecessarily
3. **Multi-step reasoning** - Gets confused after 2-3 iterations

## Recommendations

### For 1.5b Model Users:
```bash
# Use simple mode (reliable, fast)
python -m assistant --simple "your question"
```

### To Make Agent Mode Reliable:
1. **Use 3b+ model** - Better instruction following
   ```bash
   ollama pull qwen2.5-coder:3b
   python -m assistant --model qwen2.5-coder:3b "your task"
   ```

2. **Or simplify agent further** - Remove JSON requirement entirely:
   - Parse natural language responses
   - Use regex to extract tool calls
   - More forgiving format

3. **Or fine-tune** - Train on agent-specific examples

## Conclusion

**Current state:** Agent mode works for simple questions (4-5s) but remains unreliable for complex tasks.

**Best practice:** Use `--simple` mode with 1.5b model, or upgrade to 3b+ for agent features.
