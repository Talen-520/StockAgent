# StockAgent 

[![support-version](https://img.shields.io/pypi/pyversions/coredumpy)](https://img.shields.io/badge/https%3A%2F%2Fgithub.com%2FTalen-520%2FStockAgent
)
[![Download](https://img.shields.io/github/downloads/Talen-520/StockAgent/total)](https://img.shields.io/github/downloads/Talen-520/StockAgent/total)

<p align="center">
  English
  ｜
  <a href="https://github.com/Talen-520/StockAgent/blob/main/README_CN.md">English</a>
</p>

**StockAgent is an intelligent AI-powered tool that provides real-time stock market insights, news summaries, and data analysis. Leveraging advanced AI and multiple financial APIs, it helps users quickly understand market trends and company news.**

### Tools 
- [Ollama](https://ollama.com/) - Local AI model runner

## Get Started

### 1. Clone the Repository
```bash
git clone https://github.com/Talen-520/StockAgent.git
cd StockAgent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Ollama
- Download and install  [Ollama](https://ollama.com/)
- For best experience, I don't recommend any model under 7b
- Pull open source model like qwen2.5 model, if you aren't using qwen2.5, change line 71 to correct model name under /agent.py 

```bash
ollama pull qwen2.5
```

## Run  
In terminal
```bash
python agent.py
```
Web UI
```bash
streamlit run .\src\streamlit_local.py
```

## Disclaimer 
This tool is for learning purposes only. AI could make misleading information, Always conduct your own research before making financial decisions.
