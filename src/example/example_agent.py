from typing import List, Dict, Any, Optional, Union
from ollama import chat
from ollama import ChatResponse
from src.tools import scrape_yahoo_finance_news

# agent tools
def stock_news(stock: str) -> str:
    """
    Summarize news articles for a given stock symbol.

    Args:
        stock (str): The stock ticker symbol (e.g., "NVDA").

    Returns:
        str: Summarized news articles or an error message.
    """
    print("task transferred to stock agent")
    try:
        articles: List[Dict[str, Any]] = scrape_yahoo_finance_news(stock)
        summary_prompt: str = f"""
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
        error_message: str = f"Error retrieving or summarizing news for {stock}: {str(e)}"
        print(error_message) 
        return error_message

# Tool definitions
stock_news_tool: Dict[str, Any] = {
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
    def __init__(self) -> None:
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt: str = """
        You are an AI assistant.
        """

    def determine_tool_necessity(self, prompt: str) -> List[Dict[str, Any]]:
        prompt_lower: str = prompt.lower()
        
        tools: List[Dict[str, Any]] = []
        if any(stock_keyword in prompt_lower for stock_keyword in ['stock', 'price', 'market', 'share', 'trade', 'news']):
            tools.append(stock_news_tool) 
        return tools

    def select_most_relevant_tool(self, tools: List[Dict[str, Any]], prompt: str) -> List[Dict[str, Any]]:
        prompt_lower: str = prompt.lower()
        tool_priority: Dict[str, List[str]] = {
            'stock_news': ['news', 'article', 'story'],
        }
        
        for tool_name, keywords in tool_priority.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return [next(tool for tool in tools if tool['function']['name'] == tool_name)]
        
        return tools

    def process_user_input(self, user_input: str) -> str:
        # Add user input to conversation history
        self.conversation_history.append({'role': 'user', 'content': user_input})
        
        # Determine necessary tools
        necessary_tools: List[Dict[str, Any]] = self.determine_tool_necessity(user_input)
        if necessary_tools:
            necessary_tools = self.select_most_relevant_tool(necessary_tools, user_input)

        try:
            # Get response from LLM
            messages: List[Dict[str, str]] = [{'role': 'system', 'content': self.system_prompt}] + self.conversation_history
            
            response: Union[ChatResponse, Dict[str, Any]] = chat(
                'llama3.2',
                messages=messages,
                tools=necessary_tools if necessary_tools else None
            )

            # Extract the response content
            if isinstance(response, dict) and 'message' in response:
                message_content: str = response['message'].get('content', '')
                tool_calls: List[Dict[str, Any]] = response['message'].get('tool_calls', [])
            else:
                message_content: str = response.message.content
                tool_calls: List[Dict[str, Any]] = getattr(response.message, 'tool_calls', [])

            # Process tool calls if any
            if tool_calls:
                tool_results: str = self.handle_tool_calls(tool_calls, user_input)
                # Add tool results to conversation for context
                full_response: str = f"Tool Results: {tool_results}\n\n{message_content}"
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
            error_message: str = f"Error processing response: {str(e)}"
            print(error_message)
            return error_message

    def handle_tool_calls(self, tool_calls: List[Dict[str, Any]], prompt: str) -> str:
        available_functions: Dict[str, Any] = {
            # add tools here
            'stock_news': lambda stock: stock_news(stock),
        }

        results: List[str] = []
        for tool in tool_calls:
            function_to_call: Optional[Any] = available_functions.get(tool.function.name)
            if function_to_call:
                try:
                    result: str = function_to_call(**tool.function.arguments)
                    results.append(f"{tool.function.name} result: {result}")
                except Exception as e:
                    results.append(f"Error in {tool.function.name}: {str(e)}")

        return "\n".join(results)

    def clear_conversation(self) -> str:
        """Clear the conversation history"""
        self.conversation_history: List[Dict[str, str]] = []
        return "Conversation history cleared."

def main() -> None:
    assistant: ConversationalAssistant = ConversationalAssistant()
    print("Hello! I'm your Stock Agent. How can I help you today? (Type 'exit/quit' to end the conversation or 'clear' to start fresh or 'tools' to see available tools)")
    
    while True:
        user_input: str = input("\nYou: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
            print("\nAssistant: quitting the conversation.")
            break
        elif user_input.lower() in ['clear', 'reset']:
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
            response: str = assistant.process_user_input(user_input)
            print("\nAssistant:", response)
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try again.")

if __name__ == "__main__":
    main()