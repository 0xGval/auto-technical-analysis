import pandas as pd

class Ichimoku:
    def __init__(self, df, tenkan_period=9, kijun_period=26, senkou_b_period=52, displacement=26):
        self.df = df
        self.tenkan_period = tenkan_period
        self.kijun_period = kijun_period
        self.senkou_b_period = senkou_b_period
        self.displacement = displacement
        
        # Calculate all components
        self.calculate()
    
    def calculate(self):
        # Calculate Tenkan-sen
        high_tenkan = self.df['high'].rolling(window=self.tenkan_period).max()
        low_tenkan = self.df['low'].rolling(window=self.tenkan_period).min()
        self.tenkan = (high_tenkan + low_tenkan) / 2
        
        # Calculate Kijun-sen
        high_kijun = self.df['high'].rolling(window=self.kijun_period).max()
        low_kijun = self.df['low'].rolling(window=self.kijun_period).min()
        self.kijun = (high_kijun + low_kijun) / 2
        
        # Calculate Senkou Span A
        self.senkou_span_a = (self.tenkan + self.kijun) / 2
        
        # Calculate Senkou Span B
        high_span_b = self.df['high'].rolling(window=self.senkou_b_period).max()
        low_span_b = self.df['low'].rolling(window=self.senkou_b_period).min()
        self.senkou_span_b = (high_span_b + low_span_b) / 2
    
    def get_current_values(self):
        """Get current Ichimoku values"""
        return {
            'tenkan': self.tenkan.iloc[-1],
            'kijun': self.kijun.iloc[-1],
            'current_span_a': self.senkou_span_a.iloc[-self.displacement] if len(self.senkou_span_a) > self.displacement else None,
            'current_span_b': self.senkou_span_b.iloc[-self.displacement] if len(self.senkou_span_b) > self.displacement else None,
            'future_span_a': self.senkou_span_a.iloc[-1],
            'future_span_b': self.senkou_span_b.iloc[-1]
        }
    
    def analyze(self, current_price):
        """Analyze Ichimoku signals"""
        values = self.get_current_values()
        
        # Analysis results
        analysis = {}
        
        # 1. Price vs Current Cloud
        cloud_top = max(values['current_span_a'], values['current_span_b'])
        cloud_bottom = min(values['current_span_a'], values['current_span_b'])
        
        if current_price > cloud_top:
            analysis['price_vs_cloud'] = {
                'signal': 'BULLISH',
                'description': f'Price above cloud: ${current_price:.2f} > ${cloud_top:.2f}'
            }
        elif current_price < cloud_bottom:
            analysis['price_vs_cloud'] = {
                'signal': 'BEARISH',
                'description': f'Price below cloud: ${current_price:.2f} < ${cloud_bottom:.2f}'
            }
        else:
            analysis['price_vs_cloud'] = {
                'signal': 'NEUTRAL',
                'description': f'Price in cloud: ${cloud_bottom:.2f} - ${cloud_top:.2f}'
            }
        
        # 2. Future Cloud
        if values['future_span_a'] > values['future_span_b']:
            analysis['future_cloud'] = {
                'signal': 'BULLISH',
                'description': f'Span A ${values["future_span_a"]:.2f} > Span B ${values["future_span_b"]:.2f}'
            }
        else:
            analysis['future_cloud'] = {
                'signal': 'BEARISH',
                'description': f'Span A ${values["future_span_a"]:.2f} < Span B ${values["future_span_b"]:.2f}'
            }
        
        # 3. TK Cross
        if values['tenkan'] > values['kijun']:
            analysis['tk_cross'] = {
                'signal': 'BULLISH',
                'description': f'Tenkan ${values["tenkan"]:.2f} > Kijun ${values["kijun"]:.2f}'
            }
        else:
            analysis['tk_cross'] = {
                'signal': 'BEARISH',
                'description': f'Tenkan ${values["tenkan"]:.2f} < Kijun ${values["kijun"]:.2f}'
            }
        
        return values, analysis