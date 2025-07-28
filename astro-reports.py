def generate_price_data(symbol, start_date, timeframe):
    seed_str = f"{symbol}{start_date}{timeframe}"
    seed = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16) % 10**8
    random.seed(seed)
    np.random.seed(seed)
    
    base_price = {
        "AAPL": 180, "MSFT": 300, "GOOG": 140, 
        "AMZN": 120, "TSLA": 200, "NIFTY": 18000
    }.get(symbol, 100)
    
    if timeframe == "Intraday":
        dates = pd.date_range(start=start_date, periods=390, freq="1min")  # 6.5 hours
        volatility = 0.002
    elif timeframe == "Weekly":
        dates = pd.date_range(start=start_date - timedelta(days=start_date.weekday()), 
                            periods=35, freq="D")  # 5 weeks
        volatility = 0.008
    else:  # Monthly
        month_days = calendar.monthrange(start_date.year, start_date.month)[1]
        dates = pd.date_range(start=date(start_date.year, start_date.month, 1), 
                            periods=month_days, freq="D")
        volatility = 0.015
    
    # Generate price with astro-influenced movements
    movements = np.random.normal(0, volatility, len(dates))
    
    # Add astro events influence
    for i in range(1, len(dates)):
        if i % 7 == 0:  # Simulate weekly astro influence
            movements[i] += random.uniform(-0.01, 0.01)
        if dates[i].day == 15:  # Simulate monthly astro influence
            movements[i] += random.uniform(-0.02, 0.02)
    
    prices = base_price * (1 + movements.cumsum())
    
    # Create DataFrame first
    price_df = pd.DataFrame({
        "DateTime": dates,
        "Price": prices.round(2)
    })
    
    # Then calculate EMAs on the DataFrame column
    price_df["EMA_20"] = price_df["Price"].ewm(span=20).mean().round(2)
    price_df["EMA_50"] = price_df["Price"].ewm(span=50).mean().round(2)
    
    return price_df
