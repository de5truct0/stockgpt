# StockGPT CLI

A powerful command-line tool that combines real-time stock analysis with AI insights.

## Features

### Core Analysis
- Real-time stock data analysis
- Multi-stock comparison
- Technical indicators (MACD, RSI, Bollinger Bands)
- Price trend analysis
- Volume analysis
- Volatility metrics

### News & Market Context
- Multi-source news aggregation (Yahoo Finance, Finviz)
- Market sentiment analysis
- Major indices tracking (S&P 500, DOW, NASDAQ)
- Sector & industry context

### AI Integration
- OpenAI/Anthropic API support
- Smart insights generation
- Technical pattern recognition
- Investment recommendations
- Risk assessment

### Technical Features
- Intelligent caching
- Multiple API provider support
- Cross-stock correlation
- Performance rankings
- Clean console UI

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/stockgpt.git

# Navigate to directory
cd stockgpt/stockgpt-cli

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Unix/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

One-line command:
```bash
python src/stockgpt.py --api-key "your-api-key" --provider openai --symbols AAPL NVDA GOOGL --timeframe 1mo --compare
```

## Command Options

```bash
--api-key    : Your OpenAI/Anthropic API key
--provider   : API provider (openai/anthropic)
--symbols    : Stock symbols (space-separated)
--timeframe  : Analysis timeframe (1d/1wk/1mo/3mo/1y)
--compare    : Enable cross-stock comparison
```

## Project Structure

```
stockgpt-cli/
├── src/
│   ├── analysis.py        # Technical analysis
│   ├── data_fetcher.py    # Data fetching
│   ├── stockgpt.py        # Main CLI
│   ├── comparison.py      # Stock comparison
│   └── ui/
│       └── console_ui.py  # UI rendering
├── cache/                 # Data caching
└── requirements.txt       # Dependencies
```

## Features in Detail

### Technical Analysis
- Moving Averages (SMA/EMA)
- MACD (Moving Average Convergence Divergence)
- RSI (Relative Strength Index)
- Bollinger Bands
- Stochastic Oscillator
- Volume Analysis
- Volatility Metrics

### News Integration
- Real-time news from multiple sources
- Publisher diversity
- Automatic deduplication
- Smart date formatting
- Link preservation

### Market Context
- Major index tracking
- Sector analysis
- Industry comparisons
- Market cap context
- Trading metrics

### AI Analysis
- Natural language insights
- Pattern recognition
- Risk assessment
- Investment recommendations
- Market sentiment analysis

## Dependencies
- yfinance
- pandas
- requests
- beautifulsoup4
- openai/anthropic
- numpy

## Contributing
Pull requests are welcome! For major changes, please open an issue first.

## License
[MIT](https://choosealicense.com/licenses/mit/)