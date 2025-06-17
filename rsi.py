import pandas as pd
import numpy as np

class RSI:
    def __init__(self, df, length=14, smoothing_type='SMA', smoothing_length=14, 
                 upper_limit=70, middle_limit=50, lower_limit=30):
        self.df = df
        self.length = length
        self.smoothing_type = smoothing_type
        self.smoothing_length = smoothing_length
        self.upper_limit = upper_limit
        self.middle_limit = middle_limit
        self.lower_limit = lower_limit
        
        # Calculate RSI
        self.calculate()
    
    def calculate(self):
        """Calculate RSI using Wilder's Smoothing (standard EMA-based method)"""
        delta = self.df['close'].diff()
        
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Use EMA (Wilder's smoothing)
        avg_gains = gains.ewm(alpha=1/self.length, adjust=False).mean()
        avg_losses = losses.ewm(alpha=1/self.length, adjust=False).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        self.rsi = 100 - (100 / (1 + rs))
        
        # Apply smoothing if needed
        if self.smoothing_type == 'SMA':
            self.smoothed_rsi = self.rsi.rolling(window=self.smoothing_length).mean()
        elif self.smoothing_type == 'EMA':
            self.smoothed_rsi = self.rsi.ewm(span=self.smoothing_length, adjust=False).mean()
        else:
            self.smoothed_rsi = self.rsi
    
    def get_current_values(self):
        """Get current RSI values"""
        return {
            'rsi': self.rsi.iloc[-1],
            'smoothed_rsi': self.smoothed_rsi.iloc[-1],
            'upper_limit': self.upper_limit,
            'middle_limit': self.middle_limit,
            'lower_limit': self.lower_limit
        }
    
    def analyze(self):
        """Analyze RSI signals"""
        values = self.get_current_values()
        current_rsi = values['smoothed_rsi']  # Use smoothed RSI for analysis
        
        # Analysis results
        analysis = {}
        
        # 1. Overbought/Oversold Analysis
        if current_rsi >= self.upper_limit:
            analysis['condition'] = {
                'signal': 'OVERBOUGHT',
                'description': f'RSI {current_rsi:.2f} >= {self.upper_limit} (Potential reversal down)'
            }
        elif current_rsi <= self.lower_limit:
            analysis['condition'] = {
                'signal': 'OVERSOLD',
                'description': f'RSI {current_rsi:.2f} <= {self.lower_limit} (Potential reversal up)'
            }
        else:
            analysis['condition'] = {
                'signal': 'NEUTRAL',
                'description': f'RSI {current_rsi:.2f} between {self.lower_limit}-{self.upper_limit}'
            }
        
        # 2. Momentum Analysis
        if current_rsi > self.middle_limit:
            analysis['momentum'] = {
                'signal': 'BULLISH',
                'description': f'RSI {current_rsi:.2f} > {self.middle_limit} (Upward momentum)'
            }
        else:
            analysis['momentum'] = {
                'signal': 'BEARISH',
                'description': f'RSI {current_rsi:.2f} < {self.middle_limit} (Downward momentum)'
            }
        
        # 3. RSI Trend (comparing last few values)
        recent_rsi = self.smoothed_rsi.iloc[-5:]
        if len(recent_rsi) >= 5:
            if recent_rsi.iloc[-1] > recent_rsi.iloc[0]:
                analysis['trend'] = {
                    'signal': 'RISING',
                    'description': f'RSI trending up from {recent_rsi.iloc[0]:.2f} to {recent_rsi.iloc[-1]:.2f}'
                }
            else:
                analysis['trend'] = {
                    'signal': 'FALLING',
                    'description': f'RSI trending down from {recent_rsi.iloc[0]:.2f} to {recent_rsi.iloc[-1]:.2f}'
                }
        
        return values, analysis
    
    def get_divergence(self, lookback=30, peak_window=5):
        """Check for RSI divergence with price by comparing recent peaks and troughs."""
        if len(self.df) < lookback:
            return None

        # Get recent data
        recent_prices = self.df['close'].iloc[-lookback:]
        recent_rsi = self.smoothed_rsi.iloc[-lookback:]

        # Find peaks (highs) and troughs (lows)
        price_peaks = recent_prices[recent_prices.rolling(peak_window, center=True).max() == recent_prices].dropna()
        price_troughs = recent_prices[recent_prices.rolling(peak_window, center=True).min() == recent_prices].dropna()
        rsi_peaks = recent_rsi[recent_rsi.rolling(peak_window, center=True).max() == recent_rsi].dropna()
        rsi_troughs = recent_rsi[recent_rsi.rolling(peak_window, center=True).min() == recent_rsi].dropna()

        divergence = {
            'bullish_divergence': False,
            'bearish_divergence': False,
            'description': 'No divergence detected'
        }

        # Check for Bearish Divergence (higher highs in price, lower highs in RSI)
        if len(price_peaks) >= 2 and len(rsi_peaks) >= 2:
            last_price_peak = price_peaks.index[-1]
            prev_price_peak = price_peaks.index[-2]
            
            # Find corresponding RSI peaks
            last_rsi_peak = rsi_peaks[rsi_peaks.index.get_loc(last_price_peak, method='nearest')]
            prev_rsi_peak = rsi_peaks[rsi_peaks.index.get_loc(prev_price_peak, method='nearest')]

            if price_peaks.iloc[-1] > price_peaks.iloc[-2] and last_rsi_peak < prev_rsi_peak:
                divergence['bearish_divergence'] = True
                divergence['description'] = 'Bearish divergence: Price making higher highs, RSI making lower highs'
                return divergence

        # Check for Bullish Divergence (lower lows in price, higher lows in RSI)
        if len(price_troughs) >= 2 and len(rsi_troughs) >= 2:
            last_price_trough = price_troughs.index[-1]
            prev_price_trough = price_troughs.index[-2]

            # Find corresponding RSI troughs
            last_rsi_trough = rsi_troughs[rsi_troughs.index.get_loc(last_price_trough, method='nearest')]
            prev_rsi_trough = rsi_troughs[rsi_troughs.index.get_loc(prev_price_trough, method='nearest')]

            if price_troughs.iloc[-1] < price_troughs.iloc[-2] and last_rsi_trough > prev_rsi_trough:
                divergence['bullish_divergence'] = True
                divergence['description'] = 'Bullish divergence: Price making lower lows, RSI making higher lows'
                return divergence
        
        return divergence