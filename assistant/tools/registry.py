from .search_repo import SearchRepoTool
from .read_file import ReadFileTool
from .write_file import WriteFileTool
from .shell import ShellTool
from .git_tool import GitTool
from .list_files import ListFilesTool
from .apply_patch import ApplyPatchTool
from .find_symbol import FindSymbolTool
from .find_callers import FindCallersTool
from .semantic_search import SemanticSearchTool
from .edit_symbol import EditSymbolTool
from .generate_test import GenerateTestTool
from .git_diff import GitDiffTool

TOOLS = {
    "search_repo": SearchRepoTool(),
    "read_file": ReadFileTool(),
    "write_file": WriteFileTool(),
    "shell": ShellTool(),
    "git": GitTool(),
    "list_files": ListFilesTool(),
    "apply_patch": ApplyPatchTool(),
    "find_symbol": FindSymbolTool(),
    "find_callers": FindCallersTool(),
    "semantic_search": SemanticSearchTool(),
    "edit_symbol": EditSymbolTool(),
    "generate_test": GenerateTestTool(),
    "git_diff": GitDiffTool()
}

def get_tool(name):
    return TOOLS.get(name)

def get_tool_descriptions():
    return [{"name": tool.name, "description": tool.description, "arguments": tool.arguments} for tool in TOOLS.values()]
