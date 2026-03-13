import re
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
    context_parts = ["Repository Context (relevant files):\n"]
    for path in ranked_files:
        read_result = read_tool.run({"path": path, "max_lines": 40})
        if read_result["success"]:
            content = read_result["output"][:max_chars_per_file]
            context_parts.append(f"\nFile: {path}")
            context_parts.append(content)
            context_parts.append("---")
    return "\n".join(context_parts)
