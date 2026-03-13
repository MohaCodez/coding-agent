#!/usr/bin/env python3
"""Create CLI and documentation"""

import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"✓ {path}")

print("Creating CLI and documentation...\n")

# CLI main file
cli_content = """import argparse
import sys
from assistant.agent.agent_loop import run_agent
from assistant.index.symbol_index import SymbolIndex, get_shared_index
from assistant.index.semantic_index import SemanticIndex
from assistant.tools.registry import get_tool_descriptions
from assistant.agent.memory import AgentMemory

def cmd_index():
    print("Rebuilding indexes...")
    print("\\n1. Building symbol index...")
    symbol_idx = SymbolIndex()
    symbol_count = symbol_idx.build()
    print(f"   Indexed {symbol_count} symbols")
    print("\\n2. Building semantic index...")
    semantic_idx = SemanticIndex()
    chunk_count = semantic_idx.build(force=True)
    print(f"   Indexed {chunk_count} code chunks")
    print(f"\\n   Semantic index cache location:")
    print(f"   {semantic_idx.cache_file}")
    print("\\nIndexing complete!")

def cmd_stats():
    print("Index Statistics:")
    print("="*60)
    try:
        index = get_shared_index()
        stats = index.get_stats()
        print(f"\\nSymbol Index:")
        print(f"  Symbols: {stats['symbols']}")
        print(f"  Call graph edges: {stats['calls']}")
    except Exception as e:
        print(f"\\nSymbol Index: Error - {e}")
    try:
        semantic_idx = SemanticIndex()
        semantic_idx.build()
        print(f"\\nSemantic Index:")
        print(f"  Code chunks: {len(semantic_idx.documents)}")
        print(f"  Cache: {semantic_idx.cache_file}")
    except Exception as e:
        print(f"\\nSemantic Index: Error - {e}")

def cmd_tools():
    tools = get_tool_descriptions()
    print("Available Tools:")
    print("="*60)
    for tool in tools:
        print(f"\\n{tool['name']}")
        print(f"  {tool['description']}")

def cmd_memory():
    memory = AgentMemory()
    recent = memory.get_recent(10)
    if not recent:
        print("No memory entries found.")
        return
    print("Recent Assistant Memory:")
    print("="*60)
    for i, entry in enumerate(recent, 1):
        print(f"\\n{i}. {entry['summary']}")
        if entry.get('files_modified'):
            print(f"   Files: {', '.join(entry['files_modified'])}")

def main():
    parser = argparse.ArgumentParser(
        description="Local AI coding assistant powered by Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("instruction", type=str, nargs='?', help="Task or question")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--model", type=str, default=None, help="Override Ollama model")
    parser.add_argument("--max-iter", type=int, default=20, help="Max iterations")
    parser.add_argument("--no-context", action="store_true", help="Disable context")
    parser.add_argument("--index", action="store_true", help="Rebuild indexes")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--tools", action="store_true", help="List tools")
    parser.add_argument("--memory", action="store_true", help="Show memory")
    args = parser.parse_args()
    
    if args.index:
        cmd_index()
        sys.exit(0)
    if args.stats:
        cmd_stats()
        sys.exit(0)
    if args.tools:
        cmd_tools()
        sys.exit(0)
    if args.memory:
        cmd_memory()
        sys.exit(0)
    if not args.instruction:
        parser.print_help()
        sys.exit(1)
    
    try:
        result = run_agent(
            instruction=args.instruction,
            debug=args.debug,
            max_iterations=args.max_iter,
            model=args.model,
            use_context=not args.no_context
        )
        if not args.debug:
            print(result)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\\n\\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
"""

create_file("assistant/cli/main.py", cli_content)

# Main entry point
main_content = """from assistant.cli.main import main

if __name__ == "__main__":
    main()
"""
create_file("assistant/__main__.py", main_content)

# README
readme_content = """# Local AI Coding Assistant

A terminal-based AI coding assistant that runs entirely on your machine using Ollama.

## Quick Start

bash
# Install Ollama and pull model
ollama pull qwen2.5-coder:3b

# Run assistant
python -m assistant "explain this project"
python -m assistant --tools
python -m assistant --stats

## Features

- Fully local (no cloud services)
- 13+ specialized tools
- AST-based code understanding
- Semantic search with embeddings
- Safe code editing with patches
- Self-reflection and planning
- Persistent memory

## Requirements

- Python 3.8+
- Ollama (https://ollama.ai)
- ripgrep
- Git

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
"""
create_file("README.md", readme_content)

# .gitignore
gitignore_content = """.assistant/
__pycache__/
*.pyc
*.pyo
.Python
*.egg-info/
.pytest_cache/
.venv/
venv/
.DS_Store
"""
create_file(".gitignore", gitignore_content)

print("\n✓ CLI and documentation created!")
print("\n" + "="*60)
print("PROJECT SETUP COMPLETE!")
print("="*60)
print("\nNext steps:")
print("1. Install Ollama: https://ollama.ai")
print("2. Pull model: ollama pull qwen2.5-coder:3b")
print("3. Test: python -m assistant --tools")
print("4. Try: python -m assistant 'explain this project'")
print("\nOptional:")
print("- Semantic search: ollama pull nomic-embed-text")
print("- Build indexes: python -m assistant --index")
