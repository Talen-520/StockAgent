import streamlit as st
import yfinance as yf
from datetime import datetime
import time
from agentDeprecated import *

def initialize_state():
    if 'financechat_assistant' not in st.session_state:  # Unique key for assistant
        st.session_state.financechat_assistant = ConversationalAssistant()
    if 'financechat_messages' not in st.session_state:  # Unique key for messages
        st.session_state.financechat_messages = []

def get_market_indices():
    indices = {
        "Dow Jones": "^DJI",
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Russell 2000": "^RUT",
        "VIX": "^VIX"
    }
    data = {}
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            current = ticker.history(period='1d', interval='1m')
            if not current.empty:
                data[name] = {
                    'price': current['Close'].iloc[-1],
                    'change': current['Close'].iloc[-1] - current['Open'].iloc[0],
                    'change_percent': ((current['Close'].iloc[-1] - current['Open'].iloc[0]) / current['Open'].iloc[0] * 100)
                }
        except Exception as e:
            st.error(f"Error fetching {name}: {str(e)}")
    return data

def show_tools():
    tools = [
        tool['function']['name'] 
        for tool in [stock_news_tool]  
    ]
    
    disabled = [
        tool['function']['name'] 
        for tool in [get_time_series_daily_tool, get_time_series_daily_and_plot_tool, get_weather_tool]
    ]
    
    st.info(f"Available Tools: {', '.join(tools)}" )
    st.warning(f"Disabled Tools: {', '.join(disabled)}", )

def main():
    st.markdown(
        """
        <h1 style="font-size: 28px; margin-bottom: 20px;">
            Stock Market Dashboard & Assistant
        </h1>
        """,
        unsafe_allow_html=True
    )
    
    initialize_state()

    # Market indices dashboard
    indices_data = get_market_indices()
    
    # Create a grid layout with columns
    cols = st.columns(len(indices_data))
    
    for idx, (name, data) in enumerate(indices_data.items()):
        with cols[idx]:
            # Use st.markdown with custom HTML for styling
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <div style="font-size: 18px; font-weight: bold; margin-bottom: 5px;">
                        {name}
                    </div>
                    <div style="font-size: 16px; color: {'red' if data['change_percent'] < 0 else 'green'}; margin-bottom: 5px;">
                        {data['change_percent']:.2f}%
                    </div>
                    <div style="font-size: 16px; margin-bottom: 5px;">
                        {data['price']:,.2f}
                    </div>
                    <div style="font-size: 14px; color: {'red' if data['change'] < 0 else 'green'};">
                        {data['change']:+.2f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Display last updated time
    st.markdown(
        f"""
        <div style="font-size: 14px; color: gray; text-align: center; margin-top: 10px;">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            <br>
            Refresh every 5 seconds
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.divider()
    
    # Initialize state with unique keys
    initialize_state()

    # Chat input with unique key
    user_input = st.chat_input("Enter your message", key="financechat_input")
    
    if user_input:
        if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
            st.stop()
        elif user_input.lower() in ['clear', 'reset']:
            st.session_state.financechat_messages = []  # Use unique key
            st.session_state.financechat_assistant.clear_conversation()  # Use unique key
        elif user_input == 'tools':
            show_tools()
        else:
            try:
                st.session_state.financechat_messages.append({"role": "user", "content": user_input})  # Use unique key
                response = st.session_state.financechat_assistant.process_user_input(user_input)  # Use unique key
                st.session_state.financechat_messages.append({"role": "assistant", "content": response})  # Use unique key
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Display chat history
    for message in st.session_state.financechat_messages:  # Use unique key
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Auto-refresh
    time.sleep(5)
    st.rerun()

if __name__ == "__main__":
    main()