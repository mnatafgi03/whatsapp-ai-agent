from duckduckgo_search import DDGS


def web_search(query: str) -> str:
    """Search the web using DuckDuckGo and return top results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))

        if not results:
            return f"No results found for: {query}"

        lines = []
        for r in results:
            lines.append(f"• {r['title']}\n  {r['body']}")

        return f"Search results for '{query}':\n\n" + "\n\n".join(lines)

    except Exception as e:
        return f"Search error: {str(e)}"
