from lxml import html

def parse_results(raw_results: list) -> list:
    seen_urls = set()
    parsed = []

    for item in raw_results:
        content = item.get("content", "")
        if content:
            tree = html.fromstring(content)
            content = tree.text_content().strip()

        url = item.get("url", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        published = item.get("publishedDate")
        if published:
            try:
                from datetime import datetime
                published = datetime.fromisoformat(published.replace("Z", "+00:00"))
                published = published.strftime("%Y-%m-%d")
            except (ValueError, AttributeError):
                published = None

        parsed.append({
            "title": item.get("title", "Untitled"),
            "url": url,
            "snippet": content[:500] if content else "",
            "engine": item.get("engine", "unknown"),
            "publishedDate": published
        })

    return parsed