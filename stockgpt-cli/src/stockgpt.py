import argparse
import sys
from datetime import datetime, timedelta
from data_fetcher import fetch_stock_data, fetch_news
from analysis import analyze_data
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.table import Table
from typing import Dict, Any
import json
import os

def parse_arguments():
    parser = argparse.ArgumentParser(description="StockGPT: Analyze stock data and generate insights.")
    parser.add_argument('--api-key', required=True, help='API key for the Anthropic API')
    parser.add_argument('--symbol', required=True, help='Stock symbol to analyze')
    parser.add_argument('--timeframe', required=True, help='Timeframe for the analysis (e.g., 1d, 5d, 1mo, 3mo, 6mo, 1y)')

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

def print_beautified_analysis(symbol: str, timeframe: str, start_date: str, end_date: str, insights: str):
    console = Console()
    console.print(Panel(f"Insights for [bold]{symbol}[/bold] over the past {timeframe} ({start_date} to {end_date}):\n\n{insights}"))

class StockGPT:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)

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
                # If there's an error reading the cache, we'll just generate new insights
                pass

        prompt = f"""\
    Take a deep breath and think step by step. You are a CFA certified expert financial analyst who helps portfolio managers with research. Your task is to extract the most accurate and relevant financial information. Read the documents carefully, because I'm going to ask you to extract relevant financial information about the stock. Analyze the following stock data for {symbol} over a {timeframe} period and provide insights and recommendations:
    Guidelines:
    - Identify key bullet points from the documents that are most relevant to answering the question.
    - If there are no relevant points, respond with 'No relevant information.'
    - Answer the question succinctly and avoid verbatim quotes or references.
    - Give a final detailed overview with recent happenings with the stock.

    - Average Price: ${analysis['avg_price']}
    - Price Change: ${analysis['price_change']} ({analysis['price_change_pct']}%)
    - Average Volume: {analysis['avg_volume']}
    - Trend: {analysis['trend']}
    - Max Daily Gain: {analysis['max_daily_gain']}%
    - Max Daily Loss: {analysis['max_daily_loss']}%
    - MACD: {analysis['macd']}
    - MACD Signal: {analysis['macd_signal']}
    - RSI: {analysis['rsi']}
    - Bollinger Bands:
        - Upper: {analysis['bb_upper']}
        - Middle: {analysis['bb_middle']}
        - Lower: {analysis['bb_lower']}
    - Stochastic Oscillator:
        - %K: {analysis['stoch_k']}
        - %D: {analysis['stoch_d']}
        News Headlines:
        """
        for item in news:
            prompt += f"- {item['title']} ({item['link']})\n"

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4096,
            temperature=0,
            messages=messages
        )

        insights = response.content[0].text

        # Cache the insights
        with open(cache_file, 'w') as f:
            json.dump({'analysis': analysis, 'news': news, 'insights': insights}, f)

        return insights

def main():
    args = parse_arguments()
    
    try:
        validate_inputs(args.symbol)
        stock_gpt = StockGPT(args.api_key)

        start_date, end_date = get_date_range(args.timeframe)
        stock_data = fetch_stock_data(args.symbol, start_date, end_date)
        analysis = analyze_data(stock_data)
        news = fetch_news(args.symbol)
        
        # Convert analysis values to strings and round floats
        analysis = {k: f"{float(v):.2f}" if isinstance(v, (float, int)) else str(v) for k, v in analysis.items()}
        
        insights = stock_gpt.generate_insights(args.symbol, analysis, args.timeframe, news)

        print_beautified_analysis(args.symbol, args.timeframe, start_date, end_date, insights)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Input error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Runtime error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()