# StockAgent 

## Overview
StockAgent is an intelligent AI-powered tool that provides real-time stock market insights, news summaries, and data analysis. Leveraging advanced AI and multiple financial APIs, it helps users quickly understand market trends and company news.

## Features 
- Real-time stock news summarization
- Daily stock price tracking
- Weather information retrieval
- AI-powered intelligent information processing
- Flexible tool selection based on user queries

## Prerequisites 

### System Requirements
- Python 3.8+
- Pip package manager

### Tools and Platforms
- [Ollama](https://ollama.com/) - Local AI model runner
- Alpha Vantage API (for stock data)
- OpenWeatherMap API (for weather information)

## Installation 

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/StockAgent.git
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

#### Option A: Manual Installation
```bash
pip install matplotlib beautifulsoup4 requests ollama python-dotenv
```

#### Option B: Using requirements.txt
```bash
pip install -r requirements.txt
```

### 4. API Key Configuration
1. Create a `.env` file in the project root
2. Add your API keys:
```
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
OPENWEATHER_API_KEY=your_openweather_key
```

### 5. Install Ollama
- Download and install from [Ollama's official website](https://ollama.com/)
- Pull Llama3 model:
```bash
ollama pull llama3
```

## Usage 
```bash
python agent.py
```

## Example Queries 
- "What's the latest news for NVDA?"
- "Show me Apple stock prices for the last year"
- "What's the weather in New York?"

## Project Structure 📂
```
StockAgent/
│
├── agent.py          # Main application script
├── yahoo_finance_sync.py  # Web scraping module
├── .env              # API keys (git-ignored)
├── requirements.txt  # Project dependencies
└── README.md         # Project documentation
```

## API References 🌐
- [Alpha Vantage API](https://www.alphavantage.co/documentation/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Ollama Documentation](https://github.com/ollama/ollama)

## Contributing 🤝
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Disclaimer ⚖️
This tool is for learning purposes only. AI could make misleading information, Always conduct your own research before making financial decisions.
