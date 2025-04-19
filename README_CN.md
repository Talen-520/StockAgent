# StockAgent 股票智能助手

[![support-version](https://img.shields.io/pypi/pyversions/coredumpy)](https://img.shields.io/badge/https%3A%2F%2Fgithub.com%2FTalen-520%2FStockAgent
)
[![Download](https://img.shields.io/github/downloads/Talen-520/StockAgent/total)](https://img.shields.io/github/downloads/Talen-520/StockAgent/total)

<p align="center">
  中文
  ｜
  <a href="https://github.com/Talen-520/StockAgent/blob/main/README.md">English</a>
</p>

**StockAgent 是一个开源的AI工具，通过向开源模型提供工具实现股票市场洞察、新闻摘要和数据分析、帮助用户快速理解市场趋势和公司新闻。**
### 工具  
- [Ollama](https://ollama.com/) - 本地AI模型运行环境

## 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/Talen-520/StockAgent.git
cd StockAgent
```

### 2. 安装依赖 

```bash
pip install -r requirements.txt
```

### 3. 安装Ollama
- 下载安装  [Ollama](https://ollama.com/)
- 为了最佳体验，不建议使用小于7b的模型
- 拉取开源模型如qwen2.5
- 如果不使用qwen2.5，请修改/agent.py第71行为正确的模型名称

```bash
ollama pull qwen2.5
```

## 运行  
终端运行
```bash
python agent.py
```
网页端
```bash
streamlit run .\src\streamlit_local.py
```

## Disclaimer 
本工具仅用于学习目的。AI可能产生误导性信息。在做出任何投资决策前，请务必进行自主研究。

