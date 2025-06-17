import ccxt
import pandas as pd
from ichimoku import Ichimoku
from rsi import RSI
from fractals import WilliamsFractals
from ma_cross import MACross
import numpy as np

def get_color_code(signal):
    """Return color code based on signal"""
    colors = {
        'BULLISH': '\033[92m',  # Green
        'BEARISH': '\033[91m',  # Red
        'NEUTRAL': '\033[93m',  # Yellow
        'OVERBOUGHT': '\033[91m',  # Red
        'OVERSOLD': '\033[92m',  # Green
        'RISING': '\033[92m',  # Green
        'FALLING': '\033[91m',  # Red
        'BREAKOUT': '\033[92m',  # Green
        'BREAKDOWN': '\033[91m',  # Red
        'RANGE': '\033[93m',  # Yellow
        'UPTREND': '\033[92m',  # Green
        'DOWNTREND': '\033[91m',  # Red
        'MIXED': '\033[93m',  # Yellow
        'ABOVE_BOTH': '\033[92m',  # Green
        'BELOW_BOTH': '\033[91m',  # Red
        'BETWEEN': '\033[93m',  # Yellow
        'STRONG_BULLISH': '\033[92m',  # Green
        'STRONG_BEARISH': '\033[91m',  # Red
        'BULLISH_BIAS': '\033[92m',  # Green
        'BEARISH_BIAS': '\033[91m',  # Red
    }
    return colors.get(signal, '')

def print_ichimoku_analysis(symbol, current_price, values, analysis):
    """Print formatted Ichimoku analysis"""
    print(f"\n{'='*50}")
    print(f"{symbol} ICHIMOKU ANALYSIS")
    print(f"{'='*50}")
    print(f"Price: ${current_price:.2f}")
    print(f"Tenkan: ${values['tenkan']:.2f}")
    print(f"Kijun: ${values['kijun']:.2f}")
    print(f"\nCurrent Cloud (at price):")
    print(f"Span A: ${values['current_span_a']:.2f}")
    print(f"Span B: ${values['current_span_b']:.2f}")
    print(f"\nFuture Cloud (30 periods ahead):")
    print(f"Span A: ${values['future_span_a']:.2f}")
    print(f"Span B: ${values['future_span_b']:.2f}")
    
    print("\n--- Ichimoku Signals ---")
    
    # 1. Price vs Cloud
    price_signal = analysis['price_vs_cloud']
    color = get_color_code(price_signal['signal'])
    print(f"1. Price vs Cloud: {color}{price_signal['signal']}\033[0m ({price_signal['description']})")
    
    # 2. Future Cloud
    future_signal = analysis['future_cloud']
    color = get_color_code(future_signal['signal'])
    print(f"2. Future cloud: {color}{future_signal['signal']}\033[0m ({future_signal['description']})")
    
    # 3. TK Cross
    tk_signal = analysis['tk_cross']
    color = get_color_code(tk_signal['signal'])
    print(f"3. TK Cross: {color}{tk_signal['signal']}\033[0m ({tk_signal['description']})")

def print_rsi_analysis(symbol, values, analysis, rsi):
    """Print formatted RSI analysis"""
    print(f"\n{'='*50}")
    print(f"{symbol} RSI ANALYSIS")
    print(f"{'='*50}")
    print(f"RSI: {values['rsi']:.2f}")
    print(f"Smoothed RSI (SMA): {values['smoothed_rsi']:.2f}")
    print(f"Levels: {values['lower_limit']}/{values['middle_limit']}/{values['upper_limit']}")
    
    print("\n--- RSI Signals ---")
    
    # 1. Condition
    condition = analysis['condition']
    color = get_color_code(condition['signal'])
    print(f"1. Condition: {color}{condition['signal']}\033[0m ({condition['description']})")
    
    # 2. Momentum
    momentum = analysis['momentum']
    color = get_color_code(momentum['signal'])
    print(f"2. Momentum: {color}{momentum['signal']}\033[0m ({momentum['description']})")
    
    # 3. Trend
    if 'trend' in analysis:
        trend = analysis['trend']
        color = get_color_code(trend['signal'])
        print(f"3. RSI Trend: {color}{trend['signal']}\033[0m ({trend['description']})")
    
    # Check for RSI divergence
    divergence = rsi.get_divergence()
    if divergence:
        print(f"\n--- RSI Divergence Check ---")
        if divergence['bullish_divergence']:
            print(f"\033[92mBULLISH DIVERGENCE\033[0m: {divergence['description']}")
        elif divergence['bearish_divergence']:
            print(f"\033[91mBEARISH DIVERGENCE\033[0m: {divergence['description']}")
        else:
            print(f"No divergence: {divergence['description']}")

def print_fractals_analysis(symbol, current_price, values, analysis):
    """Print formatted Williams Fractals analysis"""
    print(f"\n{'='*50}")
    print(f"{symbol} WILLIAMS FRACTALS ANALYSIS")
    print(f"{'='*50}")
    if values['last_up_fractal']:
        print(f"Last Resistance (Up Fractal): ${values['last_up_fractal']:.2f}")
    if values['last_down_fractal']:
        print(f"Last Support (Down Fractal): ${values['last_down_fractal']:.2f}")
    print(f"Recent Fractals Count - Up: {values['up_fractal_count']}, Down: {values['down_fractal_count']}")
    
    print("\n--- Fractal Signals ---")
    
    # 1. Position
    if 'position' in analysis:
        position = analysis['position']
        color = get_color_code(position['signal'])
        print(f"1. Price Position: {color}{position['signal']}\033[0m ({position['description']})")
    
    # 2. Fractal Trend
    if 'fractal_trend' in analysis:
        trend = analysis['fractal_trend']
        color = get_color_code(trend['signal'])
        print(f"2. Fractal Trend: {color}{trend['signal']}\033[0m ({trend['description']})")
    
    # 3. Distances
    if 'distances' in analysis:
        distances = analysis['distances']
        print(f"3. Distances: {distances['description']}")

    # 4. Recent Fractal Sequence and Dominance
    if 'recent_fractal_sequence' in analysis:
        seq_info = analysis['recent_fractal_sequence']
        print(f"4. {seq_info['description']}")

def print_ma_cross_analysis(symbol, current_price, values, analysis):
    """Print formatted MA Cross analysis"""
    print(f"\n{'='*50}")
    print(f"{symbol} MOVING AVERAGE CROSS ANALYSIS")
    print(f"{'='*50}")
    print(f"SMA Values:")
    print(f"MA10: ${values['ma_fast']:.2f}, MA50: ${values['ma_slow']:.2f}, MA200: ${values['ma_long']:.2f}")
    
    # Set 1: Short-term (10/50) Analysis
    print(f"\n--- MA Set 1 (10/50) ---")
    set1 = analysis['set1_short_term']
    
    # Cross status
    cross_color = get_color_code(set1['cross_status']['signal'])
    print(f"1. Cross Status: {cross_color}{set1['cross_status']['signal']}\033[0m ({set1['cross_status']['description']})")
    
    # Price position
    pos_color = get_color_code(set1['price_position']['signal'])
    print(f"2. Price Position: {pos_color}{set1['price_position']['signal']}\033[0m ({set1['price_position']['description']})")
    
    # Distances
    print(f"3. {set1['distances']['description']}")
    
    # Set 2: Long-term (50/200) Analysis
    print(f"\n--- MA Set 2 (50/200) ---")
    set2 = analysis['set2_long_term']
    
    # Cross status
    cross_color = get_color_code(set2['cross_status']['signal'])
    print(f"1. Cross Status: {cross_color}{set2['cross_status']['signal']}\033[0m ({set2['cross_status']['description']})")
    
    # Price position
    pos_color = get_color_code(set2['price_position']['signal'])
    print(f"2. Price Position: {pos_color}{set2['price_position']['signal']}\033[0m ({set2['price_position']['description']})")
    
    # Distances
    print(f"3. {set2['distances']['description']}")
    
    # Market Structure
    print(f"\n--- Overall Market Structure ---")
    structure = analysis['market_structure']
    struct_color = get_color_code(structure['signal'])
    print(f"{struct_color}{structure['signal']}\033[0m: {structure['description']}")

def main():
    # Initialize exchange
    exchange = ccxt.binance()
    
    # Fetch data
    symbol = 'ETH/USDT'
    timeframe = '1d'
    limit = 500
    
    # Get ticker for most recent price
    ticker = exchange.fetch_ticker(symbol)
    current_price = ticker['last']
    
    # Get OHLCV data
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Initialize and analyze Ichimoku
    ichimoku = Ichimoku(df)
    ichimoku_values, ichimoku_analysis = ichimoku.analyze(current_price)
    
    # Initialize and analyze RSI
    rsi = RSI(df, length=14, smoothing_type='SMA', smoothing_length=14)
    rsi_values, rsi_analysis = rsi.analyze()
    
    # Initialize and analyze Williams Fractals
    fractals = WilliamsFractals(df)
    fractals_values, fractals_analysis = fractals.analyze(current_price)
    
    # Initialize and analyze MA Cross
    ma_cross = MACross(df, fast_periods=[10, 50], slow_periods=[50, 200], ma_type='SMA')
    ma_values, ma_analysis = ma_cross.analyze(current_price)
    
    # Print results
    print_ichimoku_analysis(symbol, current_price, ichimoku_values, ichimoku_analysis)
    print_rsi_analysis(symbol, rsi_values, rsi_analysis, rsi)
    print_fractals_analysis(symbol, current_price, fractals_values, fractals_analysis)
    print_ma_cross_analysis(symbol, current_price, ma_values, ma_analysis)

if __name__ == "__main__":
    main()