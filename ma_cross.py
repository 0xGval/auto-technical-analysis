import pandas as pd
import numpy as np

class MACross:
    def __init__(self, df, fast_periods=[10, 50], slow_periods=[50, 200], ma_type='SMA'):
        """
        Initialize MA Cross indicator
        fast_periods: list of fast MA periods [10, 50]
        slow_periods: list of slow MA periods [50, 200]
        ma_type: 'SMA' or 'EMA'
        """
        self.df = df
        self.fast_ma_period = fast_periods[0]  # e.g., 10
        self.slow_ma_period = slow_periods[0]  # e.g., 50
        self.long_ma_period = slow_periods[1] # e.g., 200
        self.ma_type = ma_type
        
        # Calculate all MAs
        self.calculate()
    
    def calculate(self):
        """Calculate all moving averages"""
        if self.ma_type == 'SMA':
            self.ma_fast = self.df['close'].rolling(window=self.fast_ma_period).mean()
            self.ma_slow = self.df['close'].rolling(window=self.slow_ma_period).mean()
            self.ma_long = self.df['close'].rolling(window=self.long_ma_period).mean()
        else:  # EMA
            self.ma_fast = self.df['close'].ewm(span=self.fast_ma_period, adjust=False).mean()
            self.ma_slow = self.df['close'].ewm(span=self.slow_ma_period, adjust=False).mean()
            self.ma_long = self.df['close'].ewm(span=self.long_ma_period, adjust=False).mean()
    
    def get_current_values(self):
        """Get current MA values"""
        return {
            'ma_fast': self.ma_fast.iloc[-1],
            'ma_slow': self.ma_slow.iloc[-1],
            'ma_long': self.ma_long.iloc[-1]
        }
    
    def analyze(self, current_price):
        """Analyze MA cross signals and price position"""
        values = self.get_current_values()
        analysis = {}
        
        # Set 1: Short-term (e.g., 10/50) Analysis
        analysis['set1_short_term'] = self._analyze_ma_set(
            current_price, 
            values['ma_fast'], 
            values['ma_slow'], 
            str(self.fast_ma_period), 
            str(self.slow_ma_period)
        )
        
        # Set 2: Long-term (e.g., 50/200) Analysis
        analysis['set2_long_term'] = self._analyze_ma_set(
            current_price, 
            values['ma_slow'], 
            values['ma_long'], 
            str(self.slow_ma_period), 
            str(self.long_ma_period)
        )
        
        # Overall market structure
        analysis['market_structure'] = self._analyze_market_structure(current_price, values)
        
        return values, analysis
    
    def _analyze_ma_set(self, price, fast_ma, slow_ma, fast_name, slow_name):
        """Analyze a single MA set"""
        result = {}
        
        # 1. MA Cross Status
        if fast_ma > slow_ma:
            result['cross_status'] = {
                'signal': 'BULLISH',
                'description': f'{self.ma_type} {fast_name} (${fast_ma:.2f}) > {self.ma_type} {slow_name} (${slow_ma:.2f})'
            }
        else:
            result['cross_status'] = {
                'signal': 'BEARISH',
                'description': f'{self.ma_type} {fast_name} (${fast_ma:.2f}) < {self.ma_type} {slow_name} (${slow_ma:.2f})'
            }
        
        # 2. Price Position relative to MAs
        if price > fast_ma and price > slow_ma:
            result['price_position'] = {
                'signal': 'ABOVE_BOTH',
                'description': f'Price ${price:.2f} above both MAs'
            }
        elif price < fast_ma and price < slow_ma:
            result['price_position'] = {
                'signal': 'BELOW_BOTH',
                'description': f'Price ${price:.2f} below both MAs'
            }
        else:
            result['price_position'] = {
                'signal': 'BETWEEN',
                'description': f'Price ${price:.2f} between MAs'
            }
        
        # 3. Distance from MAs
        fast_distance = ((price - fast_ma) / price) * 100
        slow_distance = ((price - slow_ma) / price) * 100
        
        result['distances'] = {
            'from_fast': fast_distance,
            'from_slow': slow_distance,
            'description': f'Distance from {self.ma_type}{fast_name}: {fast_distance:.2f}%, from {self.ma_type}{slow_name}: {slow_distance:.2f}%'
        }
        
        return result
    
    def _analyze_market_structure(self, price, values):
        """Analyze overall market structure based on all MAs"""
        # Calculate relative differences as percentages
        ma_fast_slow_diff = ((values['ma_fast'] - values['ma_slow']) / values['ma_slow']) * 100
        ma_slow_long_diff = ((values['ma_slow'] - values['ma_long']) / values['ma_long']) * 100
        price_ma_long_diff = ((price - values['ma_long']) / values['ma_long']) * 100

        # Assign weights to each signal (adjust weights as needed)
        weights = {
            'ma_fast_slow': 0.3,  # Short-term trend
            'ma_slow_long': 0.3,  # Long-term trend
            'price_ma_long': 0.4  # Price vs Long-term MA
        }

        # Calculate weighted score
        weighted_score = (
            weights['ma_fast_slow'] * (1 if ma_fast_slow_diff > 0 else -1) +
            weights['ma_slow_long'] * (1 if ma_slow_long_diff > 0 else -1) +
            weights['price_ma_long'] * (1 if price_ma_long_diff > 0 else -1)
        )

        # Determine market structure based on weighted score
        if weighted_score > 0.5:
            return {
                'signal': 'STRONG_BULLISH',
                'description': 'Strong bullish alignment with weighted score > 0.5'
            }
        elif weighted_score < -0.5:
            return {
                'signal': 'STRONG_BEARISH',
                'description': 'Strong bearish alignment with weighted score < -0.5'
            }
        elif weighted_score > 0:
            return {
                'signal': 'BULLISH_BIAS',
                'description': f'Bullish bias with weighted score: {weighted_score:.2f}'
            }
        else:
            return {
                'signal': 'BEARISH_BIAS',
                'description': f'Bearish bias with weighted score: {weighted_score:.2f}'
            }
    
    def get_cross_history(self, lookback=10):
        """Get recent MA cross events"""
        crosses = {}
        
        # Check short-term crosses (e.g., 10/50)
        ma_fast_above = self.ma_fast > self.ma_slow
        crosses_fast_slow = ma_fast_above.diff()
        recent_crosses_fast_slow = crosses_fast_slow.iloc[-lookback:]
        
        # Check long-term crosses (e.g., 50/200)
        ma_slow_above = self.ma_slow > self.ma_long
        crosses_slow_long = ma_slow_above.diff()
        recent_crosses_slow_long = crosses_slow_long.iloc[-lookback:]
        
        # Find golden/death crosses
        golden_cross_fast_slow = recent_crosses_fast_slow[recent_crosses_fast_slow == 1]
        death_cross_fast_slow = recent_crosses_fast_slow[recent_crosses_fast_slow == -1]
        
        golden_cross_slow_long = recent_crosses_slow_long[recent_crosses_slow_long == 1]
        death_cross_slow_long = recent_crosses_slow_long[recent_crosses_slow_long == -1]
        
        crosses[f'{self.fast_ma_period}_{self.slow_ma_period}'] = {
            'last_golden_cross': golden_cross_fast_slow.index[-1] if not golden_cross_fast_slow.empty else None,
            'last_death_cross': death_cross_fast_slow.index[-1] if not death_cross_fast_slow.empty else None
        }
        
        crosses[f'{self.slow_ma_period}_{self.long_ma_period}'] = {
            'last_golden_cross': golden_cross_slow_long.index[-1] if not golden_cross_slow_long.empty else None,
            'last_death_cross': death_cross_slow_long.index[-1] if not death_cross_slow_long.empty else None
        }
        
        return crosses