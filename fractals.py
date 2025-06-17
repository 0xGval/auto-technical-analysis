import pandas as pd
import numpy as np

class WilliamsFractals:
    def __init__(self, df, period=2):
        """
        Initialize Williams Fractals
        period: number of bars on each side (default 2 for standard 5-bar pattern)
        """
        self.df = df
        self.period = period
        self.calculate()
    
    def calculate(self):
        """Calculate Williams Fractals using a vectorized approach"""
        n = self.period
        window_size = 2 * n + 1

        # High Fractals (Bearish)
        self.df['fractal_up'] = self.df['high'].rolling(window=window_size, center=True).max()
        self.df['fractal_up'] = np.where(self.df['high'] == self.df['fractal_up'], self.df['high'], np.nan)
        
        # Down Fractals (Bullish)
        self.df['fractal_down'] = self.df['low'].rolling(window=window_size, center=True).min()
        self.df['fractal_down'] = np.where(self.df['low'] == self.df['fractal_down'], self.df['low'], np.nan)
        
        # Get last fractals for support/resistance
        self.last_up_fractal = self.df['fractal_up'].dropna().iloc[-1] if not self.df['fractal_up'].dropna().empty else None
        self.last_down_fractal = self.df['fractal_down'].dropna().iloc[-1] if not self.df['fractal_down'].dropna().empty else None
        
        # Get recent fractals for analysis
        self.recent_up_fractals = self.df['fractal_up'].dropna().tail(5).tolist()
        self.recent_down_fractals = self.df['fractal_down'].dropna().tail(5).tolist()
    
    def get_current_values(self):
        """Get current fractal values"""
        return {
            'last_up_fractal': self.last_up_fractal,
            'last_down_fractal': self.last_down_fractal,
            'recent_up_fractals': self.recent_up_fractals,
            'recent_down_fractals': self.recent_down_fractals,
            'up_fractal_count': len(self.recent_up_fractals),
            'down_fractal_count': len(self.recent_down_fractals)
        }
    
    def analyze(self, current_price):
        """Analyze fractal patterns and signals"""
        values = self.get_current_values()
        analysis = {}
        
        # 1. Support/Resistance Analysis
        if values['last_up_fractal'] and values['last_down_fractal']:
            if current_price > values['last_up_fractal']:
                analysis['position'] = {
                    'signal': 'BREAKOUT',
                    'description': f'Price ${current_price:.2f} broke above resistance ${values["last_up_fractal"]:.2f}'
                }
            elif current_price < values['last_down_fractal']:
                analysis['position'] = {
                    'signal': 'BREAKDOWN',
                    'description': f'Price ${current_price:.2f} broke below support ${values["last_down_fractal"]:.2f}'
                }
            else:
                analysis['position'] = {
                    'signal': 'RANGE',
                    'description': f'Price ${current_price:.2f} between support ${values["last_down_fractal"]:.2f} and resistance ${values["last_up_fractal"]:.2f}'
                }
        
        # 2. Fractal Trend Analysis
        if len(values['recent_up_fractals']) >= 2 and len(values['recent_down_fractals']) >= 2:
            # Check if fractals are making higher highs/lows or lower highs/lows
            up_trend = values['recent_up_fractals'][-1] > values['recent_up_fractals'][0]
            down_trend = values['recent_down_fractals'][-1] > values['recent_down_fractals'][0]
            
            if up_trend and down_trend:
                analysis['fractal_trend'] = {
                    'signal': 'UPTREND',
                    'description': 'Fractals showing higher highs and higher lows'
                }
            elif not up_trend and not down_trend:
                analysis['fractal_trend'] = {
                    'signal': 'DOWNTREND',
                    'description': 'Fractals showing lower highs and lower lows'
                }
            else:
                analysis['fractal_trend'] = {
                    'signal': 'MIXED',
                    'description': 'Fractals showing mixed signals'
                }
        
        # 3. Distance from fractals
        if values['last_up_fractal'] and values['last_down_fractal']:
            distance_to_resistance = ((values['last_up_fractal'] - current_price) / current_price) * 100
            distance_to_support = ((current_price - values['last_down_fractal']) / current_price) * 100
            
            analysis['distances'] = {
                'to_resistance': distance_to_resistance,
                'to_support': distance_to_support,
                'description': f'Distance to resistance: {distance_to_resistance:.2f}%, to support: {distance_to_support:.2f}%'
            }
        
        # 4. Recent fractal sequence and dominance (last 10 actual fractals)
        recent_fractals = []
        fractal_up = self.df['fractal_up']
        fractal_down = self.df['fractal_down']
        # Go backwards through the DataFrame and collect the last 10 actual fractals
        for i in range(1, len(self.df)):
            idx = -i
            if not np.isnan(fractal_up.iloc[idx]):
                recent_fractals.append('up')
            elif not np.isnan(fractal_down.iloc[idx]):
                recent_fractals.append('down')
            if len(recent_fractals) == 10:
                break
        # If less than 10, pad with 'none'
        while len(recent_fractals) < 10:
            recent_fractals.append('none')
        # Count dominance
        up_count = recent_fractals.count('up')
        down_count = recent_fractals.count('down')
        if up_count > down_count:
            dominance = 'UP fractals dominate recent price action'
        elif down_count > up_count:
            dominance = 'DOWN fractals dominate recent price action'
        else:
            dominance = 'No clear dominance in recent fractals'
        analysis['recent_fractal_sequence'] = {
            'sequence': recent_fractals,
            'dominance': dominance,
            'description': f"Recent fractal sequence (most recent first): {', '.join(recent_fractals)}. {dominance}"
        }
        
        return values, analysis