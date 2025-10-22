# Add your custom tools here
from duckduckgo_search import DDGS

def internet_search(query: str) -> str:
    """Search the internet for information"""
    try:
        ddgs = DDGS()
        results = []
        
        for result in ddgs.text(keywords=query, max_results=5):
            results.append(f"**{result.get('title', 'No Title')}**\n{result.get('body', 'No description')}\nURL: {result.get('href', '')}\n")
        
        return "\n".join(results) if results else "No search results found."
    except Exception as e:
        return f"Search unavailable: {str(e)}"