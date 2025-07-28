import yfinance as yf

def generate_price_data(symbol, start_date, timeframe):
    # Fetch real-time base price for Gold (GC=F) or Silver (SI=F)
    if symbol in ["GOLD", "GC", "XAU"]:
        ticker = "GC=F"  # COMEX Gold Futures
    elif symbol in ["SILVER", "SI", "XAG"]:
        ticker = "SI=F"  # COMEX Silver Futures
    else:
        ticker = symbol  # Stocks like AAPL, MSFT
    
    try:
        # Fetch latest price
        data = yf.Ticker(ticker)
        hist = data.history(period="1d")  # Get latest price
        base_price = hist["Close"].iloc[-1]
    except:
        # Fallback to hardcoded prices if fetch fails
        base_price = {
            "AAPL": 180, "MSFT": 300, "GOOG": 140, 
            "AMZN": 120, "TSLA": 200, "NIFTY": 18000,
            "GOLD": 3305, "GC": 3305, "XAU": 3305,
            "SILVER": 28.50, "SI": 28.50, "XAG": 28.50
        }.get(symbol, 100)  # Default to 100 if unknown
    
    # Generate random price movements (your existing code)
    if timeframe == "Intraday":
        dates = pd.date_range(start=start_date, periods=390, freq="1min")
        volatility = 0.002
    elif timeframe == "Weekly":
        dates = pd.date_range(start=start_date - timedelta(days=start_date.weekday()), 
                            periods=35, freq="D")
        volatility = 0.008
    else:
        month_days = calendar.monthrange(start_date.year, start_date.month)[1]
        dates = pd.date_range(start=date(start_date.year, start_date.month, 1), 
                            periods=month_days, freq="D")
        volatility = 0.015
    
    movements = np.random.normal(0, volatility, len(dates))
    prices = base_price * (1 + movements.cumsum())
    
    # Generate OHLC data
    opens = prices * (1 + np.random.normal(0, 0.001, len(dates)))
    highs = prices * (1 + np.random.normal(0.002, 0.001, len(dates)))
    lows = prices * (1 + np.random.normal(-0.002, 0.001, len(dates)))
    
    return pd.DataFrame({
        "DateTime": dates,
        "Open": np.round(opens, 2),
        "High": np.round(highs, 2),
        "Low": np.round(lows, 2),
        "Close": np.round(prices, 2),
        "Volume": np.random.randint(1000, 10000, len(dates))
    })
