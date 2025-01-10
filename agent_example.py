from ollama import chat
from ollama import ChatResponse
from src.tools import scrape_yahoo_finance_news

# agent tools
def stock_news(stock):
    """
    Summarize news articles for a given stock symbol.

    Args:
        stock (str): The stock ticker symbol (e.g., "NVDA").

    Returns:
        str: Summarized news articles or an error message.
    """
    try:
        articles = scrape_yahoo_finance_news(stock)
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
        
        # Use Ollama to generate a summary, we call the model and provide the summary prompt again as the user input
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
        error_message = f"Error retrieving or summarizing news for {stock}: {str(e)}"
        print(error_message) 
        return error_message

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

class ConversationalAssistant:
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = """
        You are an AI assistant.
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
            # add tools here
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