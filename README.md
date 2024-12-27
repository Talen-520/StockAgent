# StockAgent 

## Overview
StockAgent is an intelligent AI-powered tool that provides real-time stock market insights, news summaries, and data analysis. Leveraging advanced AI and multiple financial APIs, it helps users quickly understand market trends and company news.

## Features 
- **Web UI**: Built with Streamlit for easy access.
- **Data Privacy**: All information is processed locally to protect your data.
- **Efficiency**: Grab 10 finance news articles at once to save time and effort.
- **Real-Time Summarization**: Get concise summaries of the latest stock news.
- **AI-Powered Processing**: Intelligent information processing for accurate insights.
- **Flexible Tools**: Select tools based on user queries for a tailored experience.

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

### 2. Create Virtual Environment And Install Dependencies
#### windows

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install Ollama
- Download and install from [Ollama's official website](https://ollama.com/)
- Pull model like Llama3.2 model:
```bash
ollama pull llama3.2
```

### API Key Configuration [optional]
1. Create a `.env` file in the project root
2. Add your API keys:
```
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
OPENWEATHER_API_KEY=your_openweather_key
```


## Usage 
Web UI
```bash
streamlit run .\src\webUI.py
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
