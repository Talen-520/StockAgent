import streamlit as st
from agent import *
import time

def initialize_state():
    if 'webUI_assistant' not in st.session_state:  # Unique key for assistant
        st.session_state.webUI_assistant = ConversationalAssistant()
    if 'webUI_messages' not in st.session_state:  # Unique key for messages
        st.session_state.webUI_messages = []

def show_tools():
    tools = [
        tool['function']['name'] 
        for tool in [stock_news_tool]  
    ]
    
    disabled = [
        tool['function']['name'] 
        for tool in [get_time_series_daily_tool, get_time_series_daily_and_plot_tool, get_weather_tool]
    ]
    
    available = st.info(f"Available Tools: {', '.join(tools)}" )
    unavailable_tools_msg = st.warning(f"Disabled Tools: {', '.join(disabled)}", )
    time.sleep(3)
    available.empty()
    unavailable_tools_msg.empty()
    
    
def main():
    st.title('Stock Agent Chat')
    initialize_state()

    st.markdown(
    """
    **Command Available:**  
    - `clear` - clear chat history  
    - `exit` - exit the chat  
    - `tools` - show available tools  
    """
    )

    # Chat input with unique key
    user_input = st.chat_input("Enter your message", key="webUI_input")
    # Ignore empty input
    if user_input is not None:
        user_input = user_input.strip()
    
    if user_input:
        if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
            st.stop()
        elif user_input.lower() in ['clear', 'reset']:
            st.session_state.webUI_messages = []  # Use unique key
            st.session_state.webUI_assistant.clear_conversation()  # Use unique key
        elif user_input == 'tools':
            show_tools()
        else:
            try:
                st.session_state.webUI_messages.append({"role": "user", "content": user_input})  # Use unique key
                response = st.session_state.webUI_assistant.process_user_input(user_input)  # Use unique key
                st.session_state.webUI_messages.append({"role": "assistant", "content": response})  # Use unique key
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Display chat history
    for message in st.session_state.webUI_messages:  # Use unique key
        with st.chat_message(message["role"]):
            st.write(message["content"])

if __name__ == "__main__":
    main()