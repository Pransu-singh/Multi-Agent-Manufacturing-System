from langchain.tools import tool
from duckduckgo_search import DDGS

@tool
def supplier_search(query: str) -> str:
    """Search manufacturing suppliers and market data"""
    results = DDGS().text(query, max_results=5)
    response = ""
    for r in results:
        response += f"- {r['title']}: {r['body']}\n"
    return response
