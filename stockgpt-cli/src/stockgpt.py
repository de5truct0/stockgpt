import argparse
import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

from data_fetcher import fetch_stock_data, fetch_news, get_market_context
from analysis import analyze_data
from api_providers.base import AIProvider
from api_providers.anthropic_provider import AnthropicProvider
from api_providers.openai_provider import OpenAIProvider
from ui.console_ui import StockGPTUI
from comparison import StockComparison

def parse_arguments():
    parser = argparse.ArgumentParser(description="StockGPT: Analyze stock data and generate insights.")
    parser.add_argument('--api-key', required=True, help='API key for the AI provider')
    parser.add_argument('--provider', default='anthropic', choices=['anthropic', 'openai'], 
                       help='AI provider to use (default: anthropic)')
    parser.add_argument('--symbols', required=True, nargs='+', help='Stock symbols to analyze')
    parser.add_argument('--timeframe', required=True, 
                       help='Timeframe for the analysis (e.g., 1d, 5d, 1mo, 3mo, 6mo, 1y)')
    parser.add_argument('--compare', action='store_true', help='Perform comparative analysis')
    return parser.parse_args()

def validate_inputs(symbol: str):
    """Validate the stock symbol input."""
    if not symbol.isalpha():
        raise ValueError("Invalid stock symbol. Only alphabetic characters are allowed.")

def get_date_range(timeframe: str):
    """Get the start and end dates based on the specified timeframe."""
    end_date = datetime.now()
    if timeframe == "1d":
        start_date = end_date - timedelta(days=1)
    elif timeframe == "5d":
        start_date = end_date - timedelta(days=5)
    elif timeframe == "1mo":
        start_date = end_date - timedelta(days=30)
    elif timeframe == "3mo":
        start_date = end_date - timedelta(days=90)
    elif timeframe == "6mo":
        start_date = end_date - timedelta(days=180)
    elif timeframe == "1y":
        start_date = end_date - timedelta(days=365)
    else:
        raise ValueError("Invalid timeframe. Valid options are: 1d, 5d, 1mo, 3mo, 6mo, 1y")
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

class StockGPT:
    def __init__(self, api_key: str, provider: str = "anthropic"):
        """
        Initialize StockGPT with the specified AI provider
        
        Args:
            api_key: API key for the provider
            provider: Name of the AI provider ("anthropic" or "openai")
        """
        self.provider = self._get_provider(api_key, provider)
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
        self.ui = StockGPTUI()
        self.market_context = get_market_context()
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_provider(self, api_key: str, provider: str) -> AIProvider:
        """Get the appropriate AI provider instance"""
        providers = {
            "anthropic": AnthropicProvider,
            "openai": OpenAIProvider
        }
        
        if provider not in providers:
            raise ValueError(f"Unsupported provider: {provider}. Available providers: {', '.join(providers.keys())}")
        
        return providers[provider](api_key)

    def generate_insights(self, symbol: str, analysis: Dict[str, Any], timeframe: str, news: list) -> str:
        cache_file = os.path.join(self.cache_dir, f"{symbol}_{timeframe}.json")
        
        # Check cache first
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    if cached_data['analysis'] == analysis and cached_data['news'] == news:
                        return cached_data['insights']
            except json.JSONDecodeError:
                pass

        prompt = f"""\
        Take a deep breath and think step by step. You are a CFA certified expert financial analyst who helps portfolio managers with research. Your task is to extract the most accurate and relevant financial information. Read the documents carefully, because I'm going to ask you to extract relevant financial information about the stock. Analyze the following stock data for {symbol} over a {timeframe} period and provide insights and recommendations:

        Guidelines:
        - Identify key bullet points from the documents that are most relevant to answering the question.
        - If there are no relevant points, respond with 'No relevant information.'
        - Answer the question succinctly and avoid verbatim quotes or references.
        - Give a final detailed overview with recent happenings with the stock.

        Technical Analysis:
        - Average Price: ${analysis['avg_price']}
        - Price Change: ${analysis['price_change']} ({analysis['price_change_pct']}%)
        - Average Volume: {analysis['avg_volume']}
        - Trend: {analysis['trend']}
        - Volatility (Annualized): {analysis['volatility']}%
        - Max Daily Gain: {analysis['max_daily_gain']}%
        - Max Daily Loss: {analysis['max_daily_loss']}%
        - MACD: {analysis['macd']}
        - MACD Signal: {analysis['macd_signal']}
        - RSI: {analysis['rsi']}
        - Moving Averages:
            - SMA20: {analysis.get('SMA_20', 'N/A')}
            - SMA50: {analysis.get('SMA_50', 'N/A')}
            - EMA12: {analysis.get('EMA_12', 'N/A')}
            - EMA26: {analysis.get('EMA_26', 'N/A')}
        - Bollinger Bands:
            - Upper: {analysis['bb_upper']}
            - Middle: {analysis['bb_middle']}
            - Lower: {analysis['bb_lower']}
        - Stochastic Oscillator:
            - %K: {analysis['stoch_k']}
            - %D: {analysis['stoch_d']}
        
        Company Context:
        - Sector: {analysis.get('sector', 'Unknown')}
        - Industry: {analysis.get('industry', 'Unknown')}
        - Market Cap: ${analysis.get('market_cap', 0):,.2f}
        - Volatility (Annualized): {analysis.get('Volatility', 'N/A')}
        - Average Daily Value Traded: ${analysis.get('Avg_Value_Traded', 0):,.2f}

        Market Environment:
        {self.market_context}

        News Headlines and Events:
        """
        for item in news:
            title = item.get('title', '')
            publisher = item.get('publisher', '')
            date = item.get('published_date', '')
            summary = item.get('summary', '')
            prompt += f"- {title} ({publisher}, {date})\n  Summary: {summary}\n"

        insights = self.provider.generate_insights(prompt)

        # Cache the insights
        with open(cache_file, 'w') as f:
            json.dump({'analysis': analysis, 'news': news, 'insights': insights}, f)

        return insights

    def analyze_stock(self, symbol: str, timeframe: str):
        """Perform complete stock analysis with UI feedback"""
        self.ui.display_header(symbol, timeframe)
        
        with self.ui.display_loading("Fetching stock data...") as progress:
            start_date, end_date = get_date_range(timeframe)
            stock_data = fetch_stock_data(symbol, start_date, end_date)
            progress.update(0, description="Analyzing data...")
            analysis = analyze_data(stock_data)
            
            progress.update(0, description="Fetching news...")
            news = fetch_news(symbol)
            
            progress.update(0, description="Generating insights...")
            insights = self.generate_insights(symbol, analysis, timeframe, news)
        
        # Display results
        self.ui.display_technical_indicators(analysis)
        self.ui.display_market_summary(analysis)
        self.ui.display_news(news)
        self.ui.display_insights(insights)

    def analyze_multiple_stocks(self, symbols: List[str], timeframe: str):
        """Analyze multiple stocks and optionally compare them"""
        stocks_data = {}
        analyses = {}
        
        for symbol in symbols:
            self.ui.display_header(symbol, timeframe)
            # Fetch and analyze data
            self.ui.display_loading(f"Fetching data for {symbol}...")
            start_date, end_date = get_date_range(timeframe)
            stock_data = fetch_stock_data(symbol, start_date, end_date)
            stocks_data[symbol] = stock_data
            
            self.ui.display_loading(f"Analyzing {symbol} data...")
            analysis = analyze_data(stock_data)
            analyses[symbol] = analysis
            
            self.ui.display_loading(f"Fetching news for {symbol}...")
            news = fetch_news(symbol)
            
            self.ui.display_loading(f"Generating insights for {symbol}...")
            insights = self.generate_insights(symbol, analysis, timeframe, news)
            
            # Display individual stock analysis
            self.ui.display_technical_indicators(analysis)
            self.ui.display_market_summary(analysis)
            self.ui.display_news(news)
            self.ui.display_insights(insights)
        
        # Perform comparison if multiple stocks
        if len(symbols) > 1:
            comparison = StockComparison(stocks_data)
            perf_comparison = comparison.compare_performance()
            correlations = comparison.calculate_correlations()
            rankings = comparison.rank_stocks()
            
            self.ui.display_comparison(perf_comparison, correlations, rankings)

def check_environment():
    """Verify the virtual environment and dependencies"""
    try:
        import sys
        import pkg_resources
        
        # Check if running in virtual environment
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            raise RuntimeError("Please run the application in a virtual environment")
            
        # Verify required packages
        required = {'yfinance', 'pandas', 'numpy', 'anthropic', 'openai', 'rich'}
        installed = {pkg.key for pkg in pkg_resources.working_set}
        missing = required - installed
        
        if missing:
            raise RuntimeError(f"Missing required packages: {', '.join(missing)}")
            
    except Exception as e:
        print(f"Environment check failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    check_environment()
    args = parse_arguments()
    
    try:
        # Validate all symbols
        for symbol in args.symbols:
            validate_inputs(symbol)
            
        stock_gpt = StockGPT(args.api_key, args.provider)
        
        if args.compare and len(args.symbols) > 1:
            stock_gpt.analyze_multiple_stocks(args.symbols, args.timeframe)
        else:
            # If only one stock or comparison not requested
            stock_gpt.analyze_stock(args.symbols[0], args.timeframe)

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()