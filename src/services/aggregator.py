from datetime import datetime, timedelta
from utils.detect_mode import detect
from services.parser import parse_results

def aggregate(raw_results: list, query: str, mode: str, time_range: str = "") -> dict:
    parsed = parse_results(raw_results)

    # 后端硬过滤：根据 time_range 剔除过期结果
    filtered_parsed = parsed
    if time_range:
        now = datetime.now()
        threshold = None
        if time_range == "day":
            threshold = now - timedelta(days=1)
        elif time_range == "week":
            threshold = now - timedelta(weeks=1)
        elif time_range == "month":
            threshold = now - timedelta(days=31)
        elif time_range == "year":
            threshold = now - timedelta(days=366)

        if threshold:
            # 只有当结果带有明确日期且早于阈值时，才进行过滤
            # 对于没有日期的结果（publishedDate 为 None），我们选择保留，因为无法确认其新鲜度
            filtered_parsed = []
            threshold_str = threshold.strftime("%Y-%m-%d")
            for r in parsed:
                if r["publishedDate"]:
                    if r["publishedDate"] >= threshold_str:
                        filtered_parsed.append(r)
                else:
                    filtered_parsed.append(r)

    if mode == "auto":
        mode = detect(query)

    results = [{
        "title": r["title"],
        "url": r["url"],
        "snippet": r["snippet"],
        "engine": r["engine"],
        "publishedDate": r["publishedDate"]
    } for r in filtered_parsed]

    extracted_data = None
    if mode == "extract":
        extracted_data = [{
            "title": r["title"],
            "url": r["url"],
            "keyInfo": r["snippet"][:200]
        } for r in filtered_parsed]

    return {
        "mode": mode,
        "results": results,
        "extractedData": extracted_data
    }
