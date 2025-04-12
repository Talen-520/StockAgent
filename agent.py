from ollama import ChatResponse
from src.tools import scrape_yahoo_finance_news
import asyncio
import ollama

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
    


system_prompt = f"""
        you are a helpful financial assistant. Your task is to analyze and detailed summarize news from every articles for a given stock symbol, you are able to use tools to retrieve most recent news.

        if you tool is used, you should states which tool is used

        Summary Guidelines:
        1. Highlight the most significant information from each article.
        2. Include detailed information for each article, including:
           - Title
           - Key content points
           - URL
           - Timestamp
        3. Organize the summary in a clear, easy-to-read format.
        4. Focus on factual information and recent developments.
        5. clearly state number of articles retrieved and summarized.
        Output Structure:
        - **Overview**: A brief summary of all articles.
        - **Detailed Summaries**: For each article, provide:
          - Title
          - Key content points
          - URL
          - Timestamp
        """

messages = [{'role': 'system', 'content': system_prompt}]

available_functions = {
    'stock_news': retrieve_stock_news,
}

async def call_function(tool_call):
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

async def main():
    client = ollama.AsyncClient()
    model_name = 'qwen2.5'
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        messages.append({'role': 'user', 'content': user_input})

        response: ChatResponse = await client.chat(
            model_name,
            messages=messages,
            tools=[retrieve_stock_news],
            options={
                'num_ctx': 131072   # Specify the context window size to allow longer inputs
            }
        )

         
        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                output = await call_function(tool_call)
                if output is not None:
                    messages.append(response.message)
                    messages.append({'role': 'tool', 'content': str(output), 'name': tool_call.function.name})

                    final_response = await client.chat(model_name, messages=messages)
                    print('Assistant:', final_response.message.content)
                    messages.append({'role': 'assistant', 'content': final_response.message.content})
        else:
            print('Assistant:', response.message.content)
            messages.append({'role': 'assistant', 'content': response.message.content})

        # debug line
        # print(messages)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\nGoodbye!')