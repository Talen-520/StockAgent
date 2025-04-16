import streamlit as st
import time
import asyncio
import ollama
from ollama import ChatResponse
from tools import scrape_yahoo_finance_news

# Define the system prompt
system_prompt = """
You are a helpful financial assistant. Your task is to analyze and detailed summarize news from every articles for a given stock symbol, you are able to use tools to retrieve most recent news.

If a tool is used, you should state which tool is used.

Summary Guidelines:
1. Highlight the most significant information from each article.
2. Include detailed information for each article, including:
   - Title
   - Key content points
   - URL
   - Timestamp
3. Organize the summary in a clear, easy-to-read format.
4. Focus on factual information and recent developments.
5. Clearly state number of articles retrieved and summarized.

Output Structure:
- **Overview**: A brief summary of all articles.
- **Detailed Summaries**: For each article, provide:
  - Title
  - Key content points
  - URL
  - Timestamp
"""

# Keep this function exactly as provided
def retrieve_stock_news(stock: str) -> list:
    """
    Summarize news articles for a given stock symbol.

    Args:
        stock (str): The stock ticker symbol (e.g., "NVDA").

    Returns:
        list: Summarized news articles with title,content,url and timestamp or an error message.
    """
    try:
        articles = scrape_yahoo_finance_news(stock)
        return articles  # Return the list directly

    except Exception as e:
        error_message = f"Error retrieving or summarizing news for {stock}: {str(e)}"
        print(error_message) 
        return error_message

# Define available functions
available_functions = {
    'stock_news': retrieve_stock_news,
}

# Create a class for the chat assistant
class StockChatAssistant:
    def __init__(self):
        self.client = ollama.Client()
        self.model_name = 'qwen2.5'
        self.messages = [{'role': 'system', 'content': system_prompt}]
    
    def clear_conversation(self):
        self.messages = [{'role': 'system', 'content': system_prompt}]
    
    async def call_function(self, tool_call):
        """Call the function specified in the tool call and return the output."""
        if function_to_call := available_functions.get(tool_call.function.name):
            print('Calling function:', tool_call.function.name)
            print('Arguments:', tool_call.function.arguments)
            output = function_to_call(**tool_call.function.arguments)
            print('Function output:', output)
            return output
        else:
            print('Function', tool_call.function.name, 'not found')
            return None
    
    async def async_process_user_input_streaming(self, user_input, message_placeholder):
        """Process user input asynchronously with streaming response."""
        self.messages.append({'role': 'user', 'content': user_input})
        
        # Create an AsyncClient for async operations
        async_client = ollama.AsyncClient()
        
        # Define the stock_news_tool
        stock_news_tool = {
            "type": "function",
            "function": {
                "name": "stock_news",
                "description": "Retrieve news articles for a given stock symbol",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stock": {
                            "type": "string",
                            "description": "The stock ticker symbol (e.g., 'NVDA')"
                        }
                    },
                    "required": ["stock"]
                }
            }
        }
        
        # First check if tool is needed
        stream = await async_client.chat(
            self.model_name,
            messages=self.messages,
            tools=[stock_news_tool],
            options={
                'num_ctx': 131072   # Specify the context window size to allow longer inputs
            },
            stream=False  # Not streaming for the initial check
        )
        
        if hasattr(stream.message, 'tool_calls') and stream.message.tool_calls:
            # Tool call detected, handle it first
            for tool_call in stream.message.tool_calls:
                # Update placeholder to show tool usage
                message_placeholder.markdown("_Using tool to retrieve stock information..._")
                
                output = await self.call_function(tool_call)
                if output is not None:
                    self.messages.append(stream.message)
                    self.messages.append({'role': 'tool', 'content': str(output), 'name': tool_call.function.name})
                    
                    # Now stream the final response after tool call
                    full_response = ""
                    message_placeholder.markdown("_Processing stock information..._")
                    
                    # Use streaming for the final response
                    async for chunk in await async_client.chat(
                        self.model_name,
                        messages=self.messages,
                        stream=True
                    ):
                        if hasattr(chunk, 'message') and chunk.message.content:
                            full_response += chunk.message.content
                            message_placeholder.markdown(full_response + "▌")
                    
                    # Update with final response
                    message_placeholder.markdown(full_response)
                    self.messages.append({'role': 'assistant', 'content': full_response})
                    return full_response
        else:
            # No tool call, stream directly
            full_response = ""
            
            # Start a new streaming request
            async for chunk in await async_client.chat(
                self.model_name,
                messages=self.messages,
                stream=True
            ):
                if hasattr(chunk, 'message') and chunk.message.content:
                    full_response += chunk.message.content
                    message_placeholder.markdown(full_response + "▌")
            
            # Update with final response
            message_placeholder.markdown(full_response)
            self.messages.append({'role': 'assistant', 'content': full_response})
            return full_response
    
    def process_user_input_streaming(self, user_input, message_placeholder):
        """Process user input synchronously by running async function with streaming."""
        return asyncio.run(self.async_process_user_input_streaming(user_input, message_placeholder))

def initialize_state():
    """Initialize session state variables."""
    if 'webUI_messages' not in st.session_state:
        st.session_state.webUI_messages = []
    if 'webUI_assistant' not in st.session_state:
        st.session_state.webUI_assistant = StockChatAssistant()

def show_tools():
    """Show available and disabled tools."""
    # Define disabled tools
    disabled = ["get_time_series_daily", "get_time_series_daily_and_plot", "get_weather"]
    
    available = st.info(f"Available Tools: stock_news")
    unavailable_tools_msg = st.warning(f"Disabled Tools: {', '.join(disabled)}")
    time.sleep(3)
    available.empty()
    unavailable_tools_msg.empty()

def main():
    st.title('Stock Agent Chat')
    initialize_state()

    st.markdown(
    """
    **You must run Ollama and install `qwen2.5` to use this chat.**

    **Commands Available:**  
    - `clear` - clear chat history  
    - `exit` - exit the chat  
    - `tools` - show available tools  
    """
    )
    
    # Display full chat history first
    for message in st.session_state.webUI_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input with unique key
    user_input = st.chat_input("Enter your message", key="webUI_input")
    # Ignore empty input
    if user_input is not None:
        user_input = user_input.strip()
    
    if user_input:
        if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
            st.stop()
        elif user_input.lower() in ['clear', 'reset']:
            st.session_state.webUI_messages = []
            st.session_state.webUI_assistant.clear_conversation()
            st.rerun()
        elif user_input == 'tools':
            show_tools()
        else:
            try:
                # Display user message
                with st.chat_message("user"):
                    st.write(user_input)
                st.session_state.webUI_messages.append({"role": "user", "content": user_input})
                
                # Create a placeholder for the assistant's response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("_Thinking..._")
                    
                    # Process the input with streaming
                    response = st.session_state.webUI_assistant.process_user_input_streaming(
                        user_input, message_placeholder
                    )
                
                # Add the complete response to the message history
                st.session_state.webUI_messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                import traceback
                st.error(traceback.format_exc())

if __name__ == "__main__":
    main()