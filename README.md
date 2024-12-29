# StockAgent 

**StockAgent is an intelligent AI-powered tool that provides real-time stock market insights, news summaries, and data analysis. Leveraging advanced AI and multiple financial APIs, it helps users quickly understand market trends and company news.**

### Tools and Platforms
- [Ollama](https://ollama.com/) - Local AI model runner
- Alpha Vantage API (for stock data)
- OpenWeatherMap API (for weather information)

## Get Started

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

## Run  
Web UI
```bash
streamlit run .\src\webUI.py
```

## Flask API EndPoint
```bash
http://127.0.0.1:5000/stock/{symbol}
```

## Disclaimer 
This tool is for learning purposes only. AI could make misleading information, Always conduct your own research before making financial decisions.
