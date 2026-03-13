import argparse
import sys
from assistant.agent.agent_loop import run_agent
from assistant.index.symbol_index import SymbolIndex, get_shared_index
from assistant.index.semantic_index import SemanticIndex
from assistant.tools.registry import get_tool_descriptions
from assistant.agent.memory import AgentMemory

def cmd_index():
    print("Rebuilding indexes...")
    print("\n1. Building symbol index...")
    symbol_idx = SymbolIndex()
    symbol_count = symbol_idx.build()
    print(f"   Indexed {symbol_count} symbols")
    print("\n2. Building semantic index...")
    semantic_idx = SemanticIndex()
    chunk_count = semantic_idx.build(force=True)
    print(f"   Indexed {chunk_count} code chunks")
    print(f"\n   Semantic index cache location:")
    print(f"   {semantic_idx.cache_file}")
    print("\nIndexing complete!")

def cmd_stats():
    print("Index Statistics:")
    print("="*60)
    try:
        index = get_shared_index()
        stats = index.get_stats()
        print(f"\nSymbol Index:")
        print(f"  Symbols: {stats['symbols']}")
        print(f"  Call graph edges: {stats['calls']}")
    except Exception as e:
        print(f"\nSymbol Index: Error - {e}")
    try:
        semantic_idx = SemanticIndex()
        semantic_idx.build()
        print(f"\nSemantic Index:")
        print(f"  Code chunks: {len(semantic_idx.documents)}")
        print(f"  Cache: {semantic_idx.cache_file}")
    except Exception as e:
        print(f"\nSemantic Index: Error - {e}")

def cmd_tools():
    tools = get_tool_descriptions()
    print("Available Tools:")
    print("="*60)
    for tool in tools:
        print(f"\n{tool['name']}")
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
        print(f"\n{i}. {entry['summary']}")
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
    parser.add_argument("--max-iter", type=int, default=5, help="Max iterations")
    parser.add_argument("--no-context", action="store_true", help="Disable context")
    parser.add_argument("--simple", action="store_true", help="Simple mode (no agent loop)")
    parser.add_argument("--stream", action="store_true", help="Enable streaming output")
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
        if args.simple:
            from assistant.llm.ollama_client import OllamaClient
            client = OllamaClient(model=args.model) if args.model else OllamaClient()
            # Default to streaming in simple mode
            use_stream = args.stream if hasattr(args, 'stream') else True
            result = client.chat([{"role": "user", "content": args.instruction}], stream=use_stream)
            if not use_stream:
                print(result)
        else:
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
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
