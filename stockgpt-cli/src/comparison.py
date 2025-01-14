from typing import Dict, List
import pandas as pd
import numpy as np
from analysis import analyze_data

class StockComparison:
    def __init__(self, stocks_data: Dict[str, pd.DataFrame]):
        self.stocks_data = stocks_data
        self.comparisons = {}
        
    def compare_performance(self) -> Dict:
        """Compare performance metrics across stocks"""
        performance = {}
        for symbol, data in self.stocks_data.items():
            analysis = analyze_data(data)
            performance[symbol] = {
                'price_change_pct': float(analysis['price_change_pct']),
                'avg_volume': float(analysis['avg_volume']),
                'volatility': float(analysis['volatility']),
                'rsi': float(analysis['rsi']),
                'trend': analysis['trend']
            }
        return performance
    
    def calculate_correlations(self) -> pd.DataFrame:
        """Calculate price correlations between stocks"""
        prices = pd.DataFrame()
        for symbol, data in self.stocks_data.items():
            prices[symbol] = data['Close']
        return prices.corr()
    
    def rank_stocks(self) -> Dict[str, List[str]]:
        """Rank stocks by different metrics"""
        performance = self.compare_performance()
        rankings = {
            'return': [],
            'volume': [],
            'momentum': []  # Based on RSI
        }
        
        # Rank by return
        rankings['return'] = sorted(
            performance.keys(),
            key=lambda x: performance[x]['price_change_pct'],
            reverse=True
        )
        
        # Rank by volume
        rankings['volume'] = sorted(
            performance.keys(),
            key=lambda x: performance[x]['avg_volume'],
            reverse=True
        )
        
        # Rank by momentum (RSI)
        rankings['momentum'] = sorted(
            performance.keys(),
            key=lambda x: performance[x]['rsi'],
            reverse=True
        )
        
        return rankings 