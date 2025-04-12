import streamlit as st
import requests
import re
from ollama import chat
from concurrent.futures import ThreadPoolExecutor, as_completed
from duckduckgo_search import DDGS
from functools import lru_cache

# Cache search results to avoid repeating searches
@lru_cache(maxsize=32)
def web_search(query):
    try:
        return DDGS().text(query, max_results=20) # adjust max_results as needed, each result followed by {title, href(url), description}
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

# Data clearning, alternative to Jina reader-lm
def clean_html(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # Remove non-text content (e.g., JavaScript, CSS, navigation links, or graphical elements) 
    for script in soup(["script", "style", "nav", "footer", "header","canvas",]):
        script.decompose()
    return soup.get_text(separator='\n', strip=True)

# Parallel processing with timeout control
def scrape_web(query):
    results = web_search(query)
    web_content = []
    
    def fetch_content(result):
        try:
            with requests.get(result['href'], timeout=3) as response:
                response.raise_for_status()
                return clean_html(response.text)[:5000]  # Limit content length
        except Exception as e:
            return None

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fetch_content, r) for r in results]
        for future in as_completed(futures, timeout=5):
            if content := future.result():
                web_content.append(content)
            if len(web_content) >= 10:  # Early exit if we get 10 good results
                break

    return web_content[:10]  # Return max 2 results

def handle_user_input(prompt):
    if not prompt:
        return

    with st.spinner('Analyzing...'):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Only search when needed (detect question keywords)
        if 'search' in prompt.lower() or any(w in prompt.lower() for w in ['who', 'what', 'when', 'where', 'why']):
            web_content = scrape_web(prompt)
        else:
            web_content = []

        messages = [{
            "role": "system",
            "content": "Answer concisely. Use markdown for formatting." + 
                      (f"\nWeb context: {web_content}" if web_content else "")
        }, {
            "role": "user",
            "content": prompt
        }]

        # Use faster model for response
        response = chat('deepseek-r1:7b', messages=messages, stream=True, 
                       options={'temperature': 0.5, 'num_ctx': 4096*2})

        full_response = ""
        response_container = st.empty()
        for chunk in response:
            if chunk.get('message', {}).get('content'):
                full_response += chunk['message']['content']
                response_container.markdown(full_response + "▌")

        response_container.markdown(full_response)
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})

def main():
    st.title('⚡ QuickChat with Web Search')
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Ask me anything (use 'search' for web queries)"):
        handle_user_input(prompt)

if __name__ == "__main__":
    main()