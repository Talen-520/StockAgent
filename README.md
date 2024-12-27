# StockAgent 

## Overview
StockAgent is an intelligent AI-powered tool that provides real-time stock market insights, news summaries, and data analysis. Leveraging advanced AI and multiple financial APIs, it helps users quickly understand market trends and company news.

## Features 
- Protect your data privacy, all information is processed locally
- Save time and effort by grabbing 10 finance news at once
- Real-time stock news summarization
- AI-powered intelligent information processing
- Flexible tool selection based on user queries

### Tools and Platforms
- [Ollama](https://ollama.com/) - Local AI model runner
- Alpha Vantage API (for stock data)
- OpenWeatherMap API (for weather information)

## Installation 

### 1. Clone the Repository
```bash
git clone https://github.com/Talen-520/StockAgent.git
cd StockAgent
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. API Key Configuration [optional]
1. Create a `.env` file in the project root
2. Add your API keys:
```
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
OPENWEATHER_API_KEY=your_openweather_key
```

### 5. Install Ollama
- Download and install from [Ollama's official website](https://ollama.com/)
- Pull model like Llama3.2 model:
```bash
ollama pull llama3.2
```

## Usage 
```bash
python src/agent.
python src/agent_flask.py
streamlit run .\src\web.py
```
## Flask API EndPoint
```bash
http://127.0.0.1:5000/stock/{symbol}
```
## Example Queries 
- tools
- exit
- clear
- "What's the latest news for NVDA?"
- "Show me Apple stock prices for the last year"
- "What's the weather in New York?"

## API References 
- [Alpha Vantage API](https://www.alphavantage.co/documentation/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Ollama Documentation](https://github.com/ollama/ollama)

## Disclaimer 
This tool is for learning purposes only. AI could make misleading information, Always conduct your own research before making financial decisions.
