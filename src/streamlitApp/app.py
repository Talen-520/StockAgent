import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
from ollama import Client  # Import the Ollama Client
import time

# Initialize the Ollama client to connect to the local server
ollama_client = Client(host='http://localhost:11434')

# Yahoo Finance scraping functions
def extract_article_details(url: str, headers: str) -> dict:
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('div', class_='cover-title yf-1at0uqp')
        title_text = title.text.strip() if title else "No title found"

        contents = soup.find_all('p', class_='yf-1pe5jgt')
        content_text = [content.text.strip() for content in contents if content.text.strip()]

        time_element = soup.find('time', class_='byline-attr-meta-time')
        article_time = time_element['datetime'] if time_element and time_element.has_attr('datetime') else None

        return {
            'title': title_text,
            'content': content_text,
            'url': url,
            'timestamp': article_time
        }
    except Exception as e:
        print(f"Error extracting details from {url}: {e}")
        return None

def scrape_yahoo_finance_news(stock: str) -> list:
    url = f"https://finance.yahoo.com/quote/{stock}/news/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = soup.find_all('div', class_='yf-18q3fnf')
    article_urls = [
        link.find('a')['href'] 
        for link in links 
        if link.find('a') and link.find('a').has_attr('href') and link.find('a')['href'].startswith('https://finance.yahoo.com/')
    ]

    articles = []
    for article_url in article_urls[:10]:
        article_details = extract_article_details(article_url, headers)
        if article_details:
            articles.append(article_details)

    return articles

# Tool definitions
def stock_news(stock):
    try:
        articles = scrape_yahoo_finance_news(stock)
        summary_prompt = f"""
        Analyze and summarize the following news articles (max 10) for {stock} with following, each articles includes title, content, url and timestamp, here is articles:

        {articles}

        Summary Guidelines:
        1. Provide a concise overview of the key news for {stock}
        2. Highlight the most significant information from each article
        3. Include key insights of each articles, tell user that news source from yahoo finance and how many articles you summarized 
        4. Organize the summary in a clear, easy-to-read format
        5. Focus on factual information and recent developments
        """
        
        response = ollama_client.chat(
            model='llama3.2',  
            messages=[
                {
                    'role': 'system', 
                    'content': f"You are a professional financial news summarizer. Provide a clear, informative summary of {stock} stock news."
                },
                {'role': 'user', 'content': summary_prompt},
            ],
            options={
                'num_ctx': 8192
            }
        )
        
        return response['message']['content']

    except Exception as e:
        error_message = f"Error retrieving or summarizing news for {stock}: {str(e)}"
        print(error_message) 
        return error_message

stock_news_tool = {
    'type': 'function',
    'function': {
        'name': 'stock_news',
        'description': 'Fetch the news articles for a given stock.',
        'parameters': {
            'type': 'object',
            'required': ['stock'],
            'properties': {
                'stock': {'type': 'string', 'description': 'The stock ticker symbol (e.g., "NVDA").'},
            },
        },
    },
}

class ConversationalAssistant:
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = """
        You are an AI assistant specializing in information retrieval and analysis. When responding to queries:

        1. Carefully analyze the user's question to determine if external data is absolutely required.
        2. Do NOT call tools by default. Only invoke tools when:
           - The query specifically requests real-time or current information
           - Direct data retrieval is the most efficient way to answer the question
           - The information cannot be answered from your existing knowledge
        3. If a tool can help but isn't strictly necessary, first attempt to answer using your existing knowledge.
        4. When using tools, be selective and use only the most relevant tool for the specific information needed.
        5. Maintain conversation context and refer back to previous discussions when relevant.
        6. Be engaging and conversational while remaining professional and informative.

        Your primary goal is to provide accurate, helpful responses while maintaining a natural conversation flow.
        """

    def determine_tool_necessity(self, prompt):
        prompt_lower = prompt.lower()
        tools = []
        if any(stock_keyword in prompt_lower for stock_keyword in ['stock', 'price', 'market', 'share', 'trade', 'news']):
            tools.append(stock_news_tool)
        return tools

    def select_most_relevant_tool(self, tools, prompt):
        prompt_lower = prompt.lower()
        tool_priority = {
            'stock_news': ['news', 'article', 'story'],
        }
        
        for tool_name, keywords in tool_priority.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return [next(tool for tool in tools if tool['function']['name'] == tool_name)]
        return tools

    def process_user_input(self, user_input):
        self.conversation_history.append({'role': 'user', 'content': user_input})
        necessary_tools = self.determine_tool_necessity(user_input)
        if necessary_tools:
            necessary_tools = self.select_most_relevant_tool(necessary_tools, user_input)

        try:
            messages = [{'role': 'system', 'content': self.system_prompt}] + self.conversation_history
            response = ollama_client.chat(
                model='llama3.2',
                messages=messages,
                tools=necessary_tools if necessary_tools else None
            )

            if isinstance(response, dict) and 'message' in response:
                message_content = response['message'].get('content', '')
                tool_calls = response['message'].get('tool_calls', [])
            else:
                message_content = response.message.content
                tool_calls = getattr(response.message, 'tool_calls', [])

            if tool_calls:
                tool_results = self.handle_tool_calls(tool_calls, user_input)
                full_response = f"Tool Results: {tool_results}\n\n{message_content}"
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': full_response
                })
                return full_response
            else:
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': message_content
                })
                return message_content

        except Exception as e:
            error_message = f"Error processing response: {str(e)}"
            print(error_message)
            return error_message

    def handle_tool_calls(self, tool_calls, prompt):
        available_functions = {
            'stock_news': lambda stock: stock_news(stock),
        }

        results = []
        for tool in tool_calls:
            function_to_call = available_functions.get(tool.function.name)
            if function_to_call:
                try:
                    result = function_to_call(**tool.function.arguments)
                    results.append(f"{tool.function.name} result: {result}")
                except Exception as e:
                    results.append(f"Error in {tool.function.name}: {str(e)}")

        return "\n".join(results)

    def clear_conversation(self):
        self.conversation_history = []
        return "Conversation history cleared."

# Streamlit UI components
def initialize_state():
    if 'webUI_assistant' not in st.session_state:
        st.session_state.webUI_assistant = ConversationalAssistant()
    if 'webUI_messages' not in st.session_state:
        st.session_state.webUI_messages = []

def show_tools():
    tools = [tool['function']['name'] for tool in [stock_news_tool]]
    available = st.info(f"Available Tools: {', '.join(tools)}")
    time.sleep(3)
    available.empty()

def main():
    st.title('Stock Agent Chat')
    initialize_state()

    st.markdown(
    """
    **Important: This app requires:**
    1. Ollama running locally on your machine
    2. llama3.2 model installed via Ollama

    **Available Commands:**
    - `clear` - clear chat history
    - `exit` - exit the chat
    - `tools` - show available tools

    **Current Features:**
    - Stock news summarization using local LLM
    - Real-time Yahoo Finance news scraping
    """
    )

    user_input = st.chat_input("Enter your message", key="webUI_input")
    if user_input is not None:
        user_input = user_input.strip()
    
    if user_input:
        if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
            st.stop()
        elif user_input.lower() in ['clear', 'reset']:
            st.session_state.webUI_messages = []
            st.session_state.webUI_assistant.clear_conversation()
        elif user_input == 'tools':
            show_tools()
        else:
            try:
                st.session_state.webUI_messages.append({"role": "user", "content": user_input})
                response = st.session_state.webUI_assistant.process_user_input(user_input)
                st.session_state.webUI_messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    for message in st.session_state.webUI_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

if __name__ == "__main__":
    main()