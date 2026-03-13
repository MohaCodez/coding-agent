from assistant.index.symbol_index import get_shared_index
from collections import defaultdict
from functools import lru_cache

@lru_cache(maxsize=1)
def generate_repo_map(max_lines=200):
    try:
        index = get_shared_index()
        symbols = index.list_symbols()
        if not symbols:
            return ""
        file_symbols = defaultdict(list)
        for symbol in symbols:
            file_symbols[symbol['file']].append(symbol)
        lines = ["Repository Structure Map:\n"]
        line_count = 0
        for file_path in sorted(file_symbols.keys()):
            if line_count >= max_lines:
                break
            lines.append(f"\n{file_path}")
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
        return "\n".join(lines)
    except:
        return ""
