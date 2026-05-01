const DETECT_LIST_PATTERNS = ["谁", "什么", "哪个", "多少", "何时", "哪里", "who", "what", "which", "how many", "when", "where"];
const DETECT_EXTRACT_PATTERNS = ["为什么", "怎么", "如何", "评价", "分析", "比较", "解释", "why", "how", "explain", "analyze", "compare", "evaluate"];

function detectMode(query) {
  const q = query.toLowerCase();
  if (DETECT_EXTRACT_PATTERNS.some(p => q.includes(p))) return "extract";
  if (DETECT_LIST_PATTERNS.some(p => q.includes(p))) return "list";
  return "list";
}

module.exports = detectMode;