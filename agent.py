from ollama import chat
from ollama import ChatResponse
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import os
import json
from dotenv import load_dotenv
from src.tools import scrape_yahoo_finance_news

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# 2. Function
def stock_news(stock,user_input):
    """
    Summarize news articles for a given stock symbol.

    Args:
        stock (str): The stock ticker symbol (e.g., "NVDA").
        user_input (str): The user input to generate the summary.

    Returns:
        str: Summarized news articles or an error message.
    """
    try:
        articles = scrape_yahoo_finance_news(stock)
        system_prompt = f"""
        Analyze and summarize the following news articles (max 10) for {stock}. Each article includes a title, content, URL, and timestamp. Here are the articles:

        {articles}

        Summary Guidelines:
        1. Provide a concise overview of the key news from {stock}.
        2. Highlight the most significant information from each article.
        3. Include detailed information for each article, including:
           - Title
           - Key content points
           - URL
           - Timestamp
        4. Organize the summary in a clear, easy-to-read format.
        5. Focus on factual information and recent developments.
        6. Clearly state that the news is sourced from Yahoo Finance and mention the total number of articles summarized (10).

        Output Structure:
        - **Overview**: A brief summary of all articles.
        - **Detailed Summaries**: For each article, provide:
          - Title
          - Key content points
          - URL
          - Timestamp
        """

        # Use Ollama to generate a summary, we call the model and provide the summary prompt again as the user input
        response: ChatResponse = chat(
            'llama3.2',  
            messages=[
                {
                    'role': 'system', 
                    'content': system_prompt
                },
                {'role': 'user', 'content': user_input},
            ],
            options={
                'num_ctx': 8192  # Specify the context window size to allow longer inputs
            }
        )
        
        # Return the generated summary
        return response['message']['content']

    except Exception as e:
        error_message = f"Error retrieving or summarizing news for {stock}: {str(e)}"
        print(error_message) 
        return error_message

def get_time_series_daily(symbol, api_key):
    """
    Fetch daily time series stock data for a given symbol using Alpha Vantage API.

    Args:
        symbol (str): The stock ticker symbol (e.g., "AAPL").
        api_key (str): The Alpha Vantage API key.

    Returns:
        dict: Daily time series data or an error message.
    """
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_time_series_daily_and_plot(symbol, api_key) :
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        time_series = data.get("Time Series (Daily)")
        if not time_series:
            return f"Error: No time series data found for {symbol}."

        dates = []
        closing_prices = []
        one_year_ago = datetime.now() - timedelta(days=365)
        
        for date, stats in sorted(time_series.items(), reverse=True):
            current_date = datetime.strptime(date, "%Y-%m-%d")
            if current_date < one_year_ago:
                break
            dates.append(current_date)
            closing_prices.append(float(stats["4. close"]))

        plt.figure(figsize=(12, 6))
        plt.plot(dates, closing_prices, label=f'{symbol} Closing Prices', color='blue')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.title(f'{symbol} Daily Closing Prices (Last Year)')

        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.xaxis.set_minor_locator(mdates.WeekdayLocator())

        plt.xticks(rotation=45)
        plt.grid(visible=True, which='both', linestyle='--', alpha=0.7)
        plt.legend()
        plt.tight_layout()

        filename = f"{symbol}_daily_closing_prices_last_year.png"
        plt.savefig(filename)
        plt.close()

        return f"Graph saved as {filename}."
    except requests.exceptions.RequestException as e:
        return f"API Request failed: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def get_weather(location: str, api_key: str) -> dict:
    """
    Get the current weather for a specified location using OpenWeatherMap API.

    Args:
        location (str): The city name or location to fetch weather for.
        api_key (str): The OpenWeatherMap API key.

    Returns:
        dict: Weather data including temperature, description, and more.
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric",  # Use metric system for temperature in Celsius
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Tool definitions
stock_news_tool = {
    'type': 'function',
    'function': {
        'name': 'stock_news',
        'description': 'Fetch the news articles for a given stock.',
        'parameters': {
            'type': 'object',
            'required': ['stock','user_input'],
            'properties': {
                'stock': {'type': 'string', 'description': 'The stock ticker symbol (e.g., "NVDA").'},
                'user_input': {'type': 'string', 'description': 'The user input to generate the summary.'},
            },
        },
    },
}

get_time_series_daily_tool = {
    'type': 'function',
    'function': {
        'name': 'get_time_series_daily',
        'description': 'Fetch daily stock prices for a given symbol.',
        'parameters': {
            'type': 'object',
            'required': ['symbol'],
            'properties': {
                'symbol': {'type': 'string', 'description': 'The stock ticker symbol (e.g., "AAPL").'},
            },
        },
    },
}

get_time_series_daily_and_plot_tool = {
    'type': 'function',
    'function': {
        'name': 'get_time_series_daily_and_plot',
        'description': 'Fetch daily stock prices for a given symbol and generate a graph of closing prices.',
        'parameters': {
            'type': 'object',
            'required': ['symbol'],
            'properties': {
                'symbol': {'type': 'string', 'description': 'The stock ticker symbol (e.g., "AAPL").'},
            },
        },
    },
}

get_weather_tool = {
    'type': 'function',
    'function': {
        'name': 'get_weather',
        'description': 'Fetch the current weather of a specific location.',
        'parameters': {
            'type': 'object',
            'required': ['location'],
            'properties': {
                'location': {'type': 'string', 'description': 'The name of the location (e.g., New York).'},
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
        # if any(weather_keyword in prompt_lower for weather_keyword in ['weather', 'temperature', 'forecast']):
        #    tools.append(get_weather_tool)
        
        # if any(stock_keyword in prompt_lower for stock_keyword in ['stock', 'price', 'market', 'share', 'trade', 'news']):
        #    tools.extend([stock_news_tool, get_time_series_daily_tool, get_time_series_daily_and_plot_tool])
        
        return tools

    def select_most_relevant_tool(self, tools, prompt):
        prompt_lower = prompt.lower()
        tool_priority = {
            'stock_news': ['news', 'article', 'story'],
            #'get_weather': ['weather', 'temperature', 'forecast'],
            #'get_time_series_daily_and_plot': ['graph', 'plot', 'chart', 'visualization'],
            #'get_time_series_daily': ['price', 'stock', 'value', 'market']
        }
        
        for tool_name, keywords in tool_priority.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return [next(tool for tool in tools if tool['function']['name'] == tool_name)]
        
        return tools

    def process_user_input(self, user_input):
        # Add user input to conversation history
        self.conversation_history.append({'role': 'user', 'content': user_input})
        
        # Determine necessary tools
        necessary_tools = self.determine_tool_necessity(user_input)
        if necessary_tools:
            necessary_tools = self.select_most_relevant_tool(necessary_tools, user_input)

        try:
            # Get response from LLM
            messages = [{'role': 'system', 'content': self.system_prompt}] + self.conversation_history
            
            response = chat(
                'llama3.2',
                messages=messages,
                tools=necessary_tools if necessary_tools else None
            )

            # Extract the response content
            if isinstance(response, dict) and 'message' in response:
                message_content = response['message'].get('content', '')
                tool_calls = response['message'].get('tool_calls', [])
            else:
                message_content = response.message.content
                tool_calls = getattr(response.message, 'tool_calls', [])

            # Process tool calls if any
            if tool_calls:
                tool_results = self.handle_tool_calls(tool_calls, user_input)
                # Add tool results to conversation for context
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
            'stock_news': lambda stock, user_input: stock_news(stock, user_input),
            # 'get_weather': lambda location: get_weather(location, OPENWEATHER_API_KEY),
            # 'get_time_series_daily': lambda symbol: get_time_series_daily(symbol, ALPHA_VANTAGE_API_KEY),
            # 'get_time_series_daily_and_plot': lambda symbol: get_time_series_daily_and_plot(symbol, ALPHA_VANTAGE_API_KEY),
        }

        results = []
        for tool in tool_calls:
            function_to_call = available_functions.get(tool.function.name)
            if function_to_call:
                try:
                    # Extract the arguments from the tool call
                    tool_args = tool.function.arguments
                    if isinstance(tool_args, str):
                        tool_args = json.loads(tool_args)
                    
                    # Add the user input (prompt) to the arguments if the function is stock_news
                    if tool.function.name == 'stock_news':
                        tool_args['user_input'] = prompt
                    
                    result = function_to_call(**tool_args)
                    results.append(f"{tool.function.name} result: {result}")
                except Exception as e:
                    results.append(f"Error in {tool.function.name}: {str(e)}")

        return "\n".join(results)
    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history = []
        return "Conversation history cleared."

def main():
    assistant = ConversationalAssistant()
    print("Hello! I'm your Stock Agent. How can I help you today? (Type 'exit/quit' to end the conversation or 'clear' to start fresh or 'tools' to see available tools)")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'exit' or user_input.lower() == 'quit' or user_input.lower() == 'q' or user_input.lower() == 'bye':
            print("\nAssistant: quitting the conversation.")
            break
        elif user_input.lower() == 'clear' or user_input.lower() == 'reset':
            print("\nAssistant:", assistant.clear_conversation())
            continue
        elif user_input == '':
            continue
        elif user_input == 'tools':
            print("\nAvailable Tools:", [tool['function']['name'] for tool in [
                stock_news_tool, 
                #get_time_series_daily_tool, 
                #get_time_series_daily_and_plot_tool, 
                #get_weather_tool
                ]])
            continue
            
        try:
            response = assistant.process_user_input(user_input)
            print("\nAssistant:", response)
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try again.")

if __name__ == "__main__":
    main()