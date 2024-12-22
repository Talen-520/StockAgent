# 1. Imports and Configuration
from ollama import chat
from ollama import ChatResponse
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import os
import json
from dotenv import load_dotenv
from tools import scrape_yahoo_finance_news

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# 2. Function
def stock_news(stock):
    """
    Summarize news articles for a given stock symbol.

    Args:
        stock (str): The stock ticker symbol (e.g., "NVDA").

    Returns:
        str: Summarized news articles or an error message.
    """
    try:
        # Attempt to scrape and save news articles
        articles = scrape_yahoo_finance_news(stock)
        # Prepare a structured summary prompt
        summary_prompt = f"""
        Analyze and summarize the following news articles (max 10) for {stock} with following, each articles includes title, content, url and timestamp, here is articles:

        {articles}

        Summary Guidelines:
        1. Provide a concise overview of the key news for {stock}
        2. Highlight the most significant information from each article, the article is inside of json content 
        3. Include key insights of each articles, tell user that news source from yahoo finance and how many articles you summarized 
        4. Organize the summary in a clear, easy-to-read format
        5. Focus on factual information and recent developments
        
        """
        
        # Use Ollama to generate a summary
        response: ChatResponse = chat(
            'llama3.2',  
            messages=[
                {
                    'role': 'system', 
                    'content': f"You are a professional financial news summarizer. Provide a clear, informative summary of {stock} stock news."
                },
                {'role': 'user', 'content': summary_prompt},
            ],
            options={
                'num_ctx': 8192  # Specify the context window size to allow longer inputs
            }
        )
        
        # Return the generated summary
        return response['message']['content']

    except Exception as e:
        # Comprehensive error handling
        error_message = f"Error retrieving or summarizing news for {stock}: {str(e)}"
        print(error_message)  # Log the error
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
            'required': ['stock'],
            'properties': {
                'stock': {'type': 'string', 'description': 'The stock ticker symbol (e.g., "NVDA").'},
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

# 3. Tool Definition and Selection

def determine_tool_necessity(prompt):
    """
    Analyze the prompt to decide if tools are necessary.
    Returns a list of relevant tools or an empty list.
    """
    prompt_lower = prompt.lower()
    
    # Weather-specific queries
    if any(weather_keyword in prompt_lower for weather_keyword in ['weather', 'temperature', 'forecast']):
        return [get_weather_tool]
    
    # Stock-specific queries
    if any(stock_keyword in prompt_lower for stock_keyword in ['stock', 'price', 'market', 'share', 'trade', 'news']):
        return [stock_news_tool, get_time_series_daily_tool, get_time_series_daily_and_plot_tool]
    
    return []  # Default: no tools

def select_most_relevant_tool(tools, prompt):
    """
    Intelligently select the most relevant tool based on the prompt.
    """
    prompt_lower = prompt.lower()
    
    tool_priority = {
        'get_weather': ['weather', 'temperature', 'forecast'],
        'stock_news': ['news', 'article', 'story'],
        'get_time_series_daily_and_plot': ['graph', 'plot', 'chart', 'visualization'],
        'get_time_series_daily': ['price', 'stock', 'value', 'market']
    }
    
    for tool_name, keywords in tool_priority.items():
        if any(keyword in prompt_lower for keyword in keywords):
            return [next(tool for tool in tools if tool['function']['name'] == tool_name)]
    
    return tools  # Return all tools if no specific match

def is_tool_necessary(tool_name, arguments, prompt):
    """
    Determine if a tool is truly necessary based on the prompt and arguments.
    This provides an additional layer of filtering.
    """
    prompt_lower = prompt.lower()
    
    # Weather tool specifics
    if tool_name == 'get_weather':
        return 'weather' in prompt_lower or 'temperature' in prompt_lower
    
    # Stock tools specifics
    if tool_name in ['stock_news', 'get_time_series_daily', 'get_time_series_daily_and_plot']:
        return any(keyword in prompt_lower for keyword in ['stock', 'price', 'market', 'news'])
    
    return False

# 4. Main Execution Flow

def main():
    # System Prompt with clear guidelines
    SYSTEM_PROMPT = """
    You are an AI assistant specializing in information retrieval and analysis. When responding to queries:

    1. Carefully analyze the user's question to determine if external data is absolutely required.
    2. Do NOT call tools by default. Only invoke tools when:
       - The query specifically requests real-time or current information
       - Direct data retrieval is the most efficient way to answer the question
       - The information cannot be answered from your existing knowledge
    3. If a tool can help but isn't strictly necessary, first attempt to answer using your existing knowledge.
    4. When using tools, be selective and use only the most relevant tool for the specific information needed.
    5. Explain your reasoning for using a tool before invoking it.

    Your primary goal is to provide accurate, helpful responses with minimal unnecessary external data retrieval.
    """

    # Get user input
    PROMPT = input("Enter your question here: ")

    # Determine necessary tools
    necessary_tools = determine_tool_necessity(PROMPT)

    # More intelligent tool selection
    if necessary_tools:
        necessary_tools = select_most_relevant_tool(necessary_tools, PROMPT)

    # Chat with intent detection and conditional tool passing
    response: ChatResponse = chat(
        'llama3.2',
        messages=[
            {
                'role': 'system',
                'content': SYSTEM_PROMPT,
            },
            {'role': 'user', 'content': PROMPT},
        ],
        tools=necessary_tools if necessary_tools else None  # Only pass tools if needed
    )

    # Process response
    if response.message.tool_calls:
        available_functions = {
            'stock_news': lambda stock: stock_news(stock),
            'get_weather': lambda location: get_weather(location, OPENWEATHER_API_KEY),
            'get_time_series_daily': lambda symbol: get_time_series_daily(symbol, ALPHA_VANTAGE_API_KEY),
            'get_time_series_daily_and_plot': lambda symbol: get_time_series_daily_and_plot(symbol, ALPHA_VANTAGE_API_KEY),
        }

        for tool in response.message.tool_calls:
            # Additional check: Confirm tool is truly necessary
            if is_tool_necessary(tool.function.name, tool.function.arguments, PROMPT):
                function_to_call = available_functions.get(tool.function.name)
                if function_to_call:
                    print(f'Conditionally calling function: {tool.function.name}')
                    print('Arguments:', tool.function.arguments)
                    result = function_to_call(**tool.function.arguments)
                    print('Function output:', result)
            else:
                print(f'Skipped unnecessary tool: {tool.function.name}')
    else:  # General response
        print('Response:', response.message.content)

if __name__ == "__main__":
    main()