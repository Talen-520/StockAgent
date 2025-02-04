from duckduckgo_search import DDGS

def web_search(query):
    try:
        ddgs = DDGS()
        # result in {title, href, description}
        results = ddgs.text(query, max_results=5)
        return results
    except Exception as e:
        print(f"Error during web search: {e}")
        return []

if __name__ == "__main__":
    # Perform a search
    result = web_search("what is duckduckgo")
    print(result)