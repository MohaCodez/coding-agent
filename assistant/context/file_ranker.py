import re

def rank_files(instruction, search_output, max_files=10):
    if not search_output:
        return []
    keywords = set(re.findall(r'\b\w{4,}\b', instruction.lower()))
    file_scores = {}
    lines = search_output.strip().split('\n')
    for line in lines:
        if not line:
            continue
        match = re.match(r'^([^:]+):\d+:', line)
        if match:
            file_path = match.group(1)
            file_scores[file_path] = file_scores.get(file_path, 0) + 10
    for file_path in list(file_scores.keys()):
        path_lower = file_path.lower()
        for keyword in keywords:
            if keyword in path_lower:
                file_scores[file_path] += 5
    ranked = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)
    return [path for path, score in ranked[:max_files]]
