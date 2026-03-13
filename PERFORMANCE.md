# Performance Guide

## Model: qwen2.5-coder:1.5b

### Hardware
- GPU: NVIDIA GTX 1650 (4GB)
- All 29/29 layers offloaded to GPU
- GPU utilization: 65-100% during inference

### Performance Metrics

| Mode | Response Time | Use Case |
|------|--------------|----------|
| Simple (streaming) | 2-5 seconds | Questions, explanations, code generation |
| Agent (optimized) | 5-20 seconds | Simple code analysis |
| Agent (complex) | 20-60 seconds | Multi-step tasks with tools |

### Optimizations Applied

1. **Skip Planning** - Only plan for queries mentioning code elements (saves 25s)
2. **Skip Reflection** - Only reflect when files are modified (saves 25-50s)
3. **Cache Repo Map** - Cache file tree generation (saves 2-5s)
4. **Streaming Output** - Real-time response display (better UX)

### Usage Recommendations

#### ✅ Use Simple Mode For:
```bash
python -m assistant --simple "your question"
```
- Code generation
- Explanations and tutorials
- Quick questions
- Debugging help

#### ⚠️ Agent Mode Limitations:
The 1.5b model struggles with:
- Complex JSON formatting required by agent loop
- Multi-step reasoning with tools
- Following strict agent instructions

**Recommendation:** Stick to `--simple` mode for best experience.

### Future Improvements

To make agent mode viable:
1. Use larger model (3b or 7b) for better instruction following
2. Simplify agent protocol (less strict JSON requirements)
3. Add few-shot examples in system prompt
4. Implement tool-use fine-tuning

### Comparison: Simple vs Agent Mode

```bash
# Simple mode (recommended)
$ python -m assistant --simple "write a function to reverse a string"
# Response: 3 seconds, streaming output, works perfectly

# Agent mode (experimental)
$ python -m assistant "write a function to reverse a string"
# Response: 8-15 seconds, often hits iteration limit, inconsistent
```

## Conclusion

The 1.5b model is **excellent for simple mode** but **not suitable for agent mode**. 
For agent features, consider using a larger model (3b+) or use simple mode exclusively.
