DETECT_LIST_PATTERNS = ["谁", "什么", "哪个", "多少", "何时", "哪里", "who", "what", "which", "how many", "when", "where"]
DETECT_EXTRACT_PATTERNS = ["为什么", "怎么", "如何", "评价", "分析", "比较", "解释", "why", "how", "explain", "analyze", "compare", "evaluate"]

def detect(query: str) -> str:
    q = query.lower()
    if any(p in q for p in DETECT_EXTRACT_PATTERNS):
        return "extract"
    if any(p in q for p in DETECT_LIST_PATTERNS):
        return "list"
    return "list"
