from flask import Flask, jsonify
from ollama import chat
from ollama import ChatResponse
from src.tools.yahoo_finance_sync import scrape_yahoo_finance_news
import os

app = Flask(__name__)


def stock_news(stock):
    """
    Summarize news articles for a given stock symbol.
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
                'num_ctx': 8192
            }
        )
        
        return {
            'status': 'success',
            'summary': response['message']['content'],
            #'articles': articles
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': f"Error retrieving or summarizing news for {stock}: {str(e)}"
        }

@app.route('/')
def home():
    """Return API information and available endpoints"""
    return jsonify({
        'name': 'Stock News API',
        'version': '1.0',
        'endpoints': {
            '/': 'API information (this message)',
            '/stock/<symbol>': 'Get news for a specific stock symbol'
        }
    })

@app.route('/stock/<symbol>')
def get_stock_news(symbol):
    """API endpoint to get stock news"""
    result = stock_news(symbol.upper())
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)