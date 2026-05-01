from utils.detect_mode import detect
from services.parser import parse_results

def aggregate(raw_results: list, query: str, mode: str) -> dict:
    parsed = parse_results(raw_results)

    if mode == "auto":
        mode = detect(query)

    results = [{
        "title": r["title"],
        "url": r["url"],
        "snippet": r["snippet"],
        "engine": r["engine"],
        "publishedDate": r["publishedDate"]
    } for r in parsed]

    extracted_data = None
    if mode == "extract":
        extracted_data = [{
            "title": r["title"],
            "url": r["url"],
            "keyInfo": r["snippet"][:200]
        } for r in parsed]

    return {
        "mode": mode,
        "results": results,
        "extractedData": extracted_data
    }