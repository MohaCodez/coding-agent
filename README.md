# Local AI Coding Assistant

A terminal-based AI coding assistant that runs entirely on your machine using Ollama.

## Quick Start

```bash
# Install Ollama and pull model
ollama pull qwen2.5-coder:1.5b

# Simple mode (fast, direct answers)
python -m assistant --simple "explain recursion"
python -m assistant --simple "write a function to sort a list"

# Agent mode (with tools, planning, context)
python -m assistant "analyze this project"
python -m assistant --tools
python -m assistant --stats
```

## Features

- Fully local (no cloud services)
- 13+ specialized tools
- AST-based code understanding
- Semantic search with embeddings
- Safe code editing with patches
- Self-reflection and planning
- Persistent memory
- **Simple mode** for instant responses

## Requirements

- Python 3.8+
- Ollama (https://ollama.ai)
- ripgrep
- Git

## Usage Modes

### Simple Mode (Recommended)
Fast, direct LLM responses with streaming output:
```bash
python -m assistant --simple "your question"
```
- ⚡ 2-5 seconds response time
- 📺 Real-time streaming output
- No tool execution or context building
- Perfect for: code generation, explanations, quick questions

### Agent Mode (Experimental)
Complete agent with tools, planning, and context:
```bash
python -m assistant "your task"
python -m assistant --debug "your task"  # see reasoning
```
- 🔧 Access to all 13 tools
- 📊 Repository context and search
- 🧠 Planning and self-reflection
- ⚠️ Note: 1.5b model struggles with complex agent instructions
- Perfect for: simple code analysis tasks

**Recommendation:** Use `--simple` mode for best experience with the 1.5b model.

## Tools

- search_repo, find_symbol, find_callers
- semantic_search (requires: ollama pull nomic-embed-text)
- read_file, write_file, apply_patch, edit_symbol
- generate_test, git_diff, git, shell, list_files

## Safety

- Blocked shell commands (rm -rf, sudo, curl, wget)
- Path validation (no ../.. escapes)
- Patch context validation
- Max 30% file modification per patch
- Self-reflection before finalizing changes

## Project Stats

~1,650 lines of Python | 13 tools | 3 indexes | Zero dependencies (except requests)
