# Crypto Technical Analysis Terminal Tool

A Python-based terminal tool for multi-indicator technical analysis of cryptocurrencies, featuring Ichimoku Cloud, RSI, Williams Fractals, and Moving Average Crosses. Fetches live data from Binance and prints a color-coded, human-readable summary for each indicator.

## Features

- **Ichimoku Cloud**: Analyzes trend, support/resistance, and momentum using standard parameters (9, 26, 52, 26).
- **RSI (Relative Strength Index)**: Calculates RSI with standard Wilder's Smoothing (EMA) and detects overbought/oversold conditions, momentum, trend, and price divergences.
- **Williams Fractals**: Efficiently identifies recent support/resistance levels and market trends using a vectorized calculation.
- **Moving Average Crosses**: Analyzes short-term (10/50) and long-term (50/200) SMA crossovers to determine market structure.
- **Color-coded terminal output** for quick visual interpretation.

## File Structure

```
main.py             # Entry point, orchestrates data fetching and analysis
ichimoku.py         # Ichimoku Cloud indicator logic
rsi.py              # RSI indicator logic
fractals.py         # Williams Fractals indicator logic
ma_cross.py         # Moving Average Crosses indicator logic
```

## How It Works

1. **Fetches OHLCV data** for a given symbol (default: ETH/USDT, 1-day timeframe) from Binance using `ccxt`.
2. **Builds a DataFrame** with historical price data using pandas.
3. **Calculates all indicators** using their respective classes, which encapsulate the analysis logic.
4. **Prints a detailed analysis** for each indicator, with color-coded signals (bullish, bearish, neutral, etc.).
5. **Checks for RSI divergence**, providing an additional layer of confirmation for potential reversals.

## Setup

### Requirements

- Python 3.7+
- `ccxt`
- `pandas`
- `numpy`

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  It is highly recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  Install dependencies:
    ```bash
    pip install ccxt pandas numpy
    ```

4. Create a `.gitignore` file in the root of your project with the following content to exclude the virtual environment and other unnecessary files from version control:
    ```
    # Virtual Environment
    venv/
    
    # Python cache
    __pycache__/
    *.pyc
    ```

## Usage

Run the main script from your terminal:

```bash
python main.py
```

You'll see a detailed, color-coded analysis for the latest daily candle of ETH/USDT.

## Customization

- **Change symbol/timeframe**: Edit the `symbol` and `timeframe` variables in `main.py`.
- **Adjust indicator parameters**: Modify the constructor arguments in `main.py` for each indicator class.

## Example Output

```
==================================================
ETH/USDT ICHIMOKU ANALYSIS
==================================================
Price: $2000.00
Tenkan: $1980.00
Kijun: $1950.00
...
1. Price vs Cloud:  [92mBULLISH [0m (Price above cloud: $2000.00 > $1970.00)
...
```

## Future Improvements
- Add more indicators (e.g., Bollinger Bands, MACD).
- Implement more advanced error handling and data validation.
- Allow for command-line arguments to specify symbol, timeframe, and other parameters.
- Add support for different exchanges.

## License

MIT License 
