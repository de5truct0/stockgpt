from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import pandas as pd
from typing import Dict, List

class StockGPTUI:
    def __init__(self):
        self.console = Console()
        
    def display_header(self, symbol: str, timeframe: str):
        """Display simple header"""
        self.console.print(f"\n=== Analysis for {symbol} ({timeframe}) ===\n")
        
    def display_technical_indicators(self, analysis: dict):
        """Display key technical indicators"""
        self.console.print("\nTechnical Analysis:", style="bold")
        price_change = analysis.get('price_change', 'N/A')
        price_change_pct = analysis.get('price_change_pct', 'N/A')
        avg_volume = int(float(analysis.get('avg_volume', 0)))
        rsi = analysis.get('rsi', 'N/A')
        trend = analysis.get('trend', 'N/A')
        
        self.console.print(f"Price Change: ${price_change} ({price_change_pct}%)")
        self.console.print(f"Average Volume: {avg_volume:,}")
        self.console.print(f"RSI: {rsi}")
        self.console.print(f"Trend: {trend}")
            
    def display_market_summary(self, analysis: dict):
        """Display simple market summary"""
        self.console.print("\nMarket Summary:", style="bold")
        gain = analysis.get('max_daily_gain', 'N/A')
        loss = analysis.get('max_daily_loss', 'N/A')
        self.console.print(f"Max Daily Gain: {gain}%")
        self.console.print(f"Max Daily Loss: {loss}%")
        
    def display_news(self, news: list):
        """Display recent news headlines"""
        self.console.print("\nRecent News:", style="bold")
        for item in news[:3]:
            self.console.print(f"• {item.get('title', 'No title available')}")
            
    def display_insights(self, insights: str):
        """Display AI insights"""
        self.console.print("\nAI Analysis:", style="bold")
        self.console.print(insights)
        
    def display_loading(self, message: str):
        """Simple loading message"""
        self.console.print(f"\n{message}")
        return self.console
        
    def display_comparison(self, comparison_data: Dict, correlations: pd.DataFrame, rankings: Dict):
        """Display simplified comparison"""
        self.console.print("\nStock Comparison:", style="bold")
        
        # Performance comparison
        self.console.print("\nPerformance:")
        for symbol, data in comparison_data.items():
            pct_change = data.get('price_change_pct', 0.0)
            self.console.print(f"{symbol}: {pct_change:.2f}% change")
        
        # Rankings
        self.console.print("\nRankings:")
        for metric, ranked_stocks in rankings.items():
            self.console.print(f"{metric.title()}: {' > '.join(ranked_stocks)}") 