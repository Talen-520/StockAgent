import streamlit as st
import requests
import re

from ollama import chat
from tools import web_search
from concurrent.futures import ThreadPoolExecutor # Parallel Processing for Web Scraping

# Function to extract text from html from Jina llm
def html_to_markdown(html):
    try:
        messages = [{'role': 'user', 'content': html}]
        response = chat('reader-lm:latest', messages=messages)
        print(response['message']['content'])
        return response['message']['content']
    except Exception as e:
        print(f"Error during HTML to Markdown conversion: {e}")
        return ""
    
# scrape web content
def scrape_web(query):
    results = web_search(query)
    web_content = []

    def fetch_and_convert(result):
        url = result['href']
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return html_to_markdown(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    with ThreadPoolExecutor(max_workers=5) as executor:
        web_content = list(executor.map(fetch_and_convert, results))

    # Filter out None values
    web_content = [content for content in web_content if content is not None]
    return web_content
    
def initialize_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def display_chat_history():
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Function to handle user input and model response
def handle_user_input(prompt):
    if prompt:
        st.session_state.chat_history.append({"role": "User", "content": prompt})

        with st.chat_message("User"):
            st.write(prompt)
        
        search_results = scrape_web(prompt)
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. if user provide web search content, analyze markdown provided for user question."
            },
            {
                "role": "user",
                "content":f'user question {prompt}. Web search content: {search_results}'
            }
        ]

        with st.chat_message("Model"):
            response_placeholder = st.empty()  
            full_response = ""

            # Use the Ollama chat function
            response = chat('deepseek-r1:7b', messages=messages, stream=True, options={'num_ctx': 8192})
            for chunk in response:
                if "message" in chunk and "content" in chunk["message"]:
                    full_response += chunk["message"]["content"]
                    response_placeholder.write(full_response)  

        st.session_state.chat_history.append({"role": "Model", "content": full_response})

def main():
    st.title('Chat with web-search using Ollama')

    initialize_session_state()
    display_chat_history()

    prompt = st.chat_input("Ask a question with web search")
    handle_user_input(prompt)

if __name__ == "__main__":
    main()