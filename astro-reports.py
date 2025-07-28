import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import hashlib

# App configuration
st.set_page_config(
    page_title="Astro Trading Signals",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Generate unique signals based on symbol and timeframe
def generate_signals(symbol, timeframe):
    # Create a stable seed using symbol and timeframe
    seed_str = f"{symbol}{timeframe}"
    seed = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16) % 10**8
    random.seed(seed)
    np.random.seed(seed)
    
    # Generate dates based on timeframe
    if timeframe == "Intraday":
        dates = pd.date_range(end=datetime.now(), periods=24, freq="H")
    elif timeframe == "Daily":
        dates = pd.date_range(end=datetime.now(), periods=30, freq="D")
    else:  # Weekly
        dates = pd.date_range(end=datetime.now(), periods=12, freq="W")
    
    # Generate unique price patterns
    base_price = {
        "AAPL": 180, "MSFT": 300, "GOOG": 140, 
        "AMZN": 120, "TSLA": 200
    }.get(symbol, 100)  # Default base price for custom symbols
    
    volatility = {
        "Intraday": 0.03,
        "Daily": 0.01,
        "Weekly": 0.005
    }[timeframe]
    
    prices = base_price * (1 + np.random.normal(0, volatility, len(dates))).cumsum()
    
    # Generate unique signals
    signal_strength = {
        "Intraday": 0.7,
        "Daily": 0.5,
        "Weekly": 0.3
    }[timeframe]
    
    signals = []
    for i in range(len(dates)):
        rand = random.random()
        if rand < 0.2 * signal_strength:
            signals.append("Strong Buy")
        elif rand < 0.4 * signal_strength:
            signals.append("Buy")
        elif rand > 1 - 0.2 * signal_strength:
            signals.append("Strong Sell")
        elif rand > 1 - 0.4 * signal_strength:
            signals.append("Sell")
        else:
            signals.append("Neutral")
    
    return pd.DataFrame({
        "Time": dates,
        "Price": prices.round(2),
        "Recommendation": signals,
        "Confidence %": np.random.uniform(35, 95, len(dates)).round(1)
    })

# Main app
def main():
    st.title("📈 Astro Trading Signals")
    
    # Initialize session state
    if 'symbol' not in st.session_state:
        st.session_state.symbol = "AAPL"
    if 'custom_symbol' not in st.session_state:
        st.session_state.custom_symbol = ""
    
    with st.sidebar:
        st.header("Parameters")
        
        # Symbol selection
        symbol_options = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "Custom"]
        selected_option = st.selectbox("Select Symbol", symbol_options)
        
        if selected_option == "Custom":
            custom_symbol = st.text_input("Enter Symbol", "NIFTY").strip().upper()
            if custom_symbol:
                st.session_state.symbol = custom_symbol
                st.session_state.custom_symbol = custom_symbol
        else:
            st.session_state.symbol = selected_option
        
        # Timeframe selection
        timeframe = st.selectbox("Timeframe", ["Intraday", "Daily", "Weekly"])
        
        if st.button("Generate Signals"):
            try:
                with st.spinner(f"Generating {timeframe} signals for {st.session_state.symbol}..."):
                    st.session_state.df = generate_signals(st.session_state.symbol, timeframe)
            except Exception as e:
                st.error(f"Error generating signals: {str(e)}")
                st.stop()
    
    # Display results
    if "df" in st.session_state:
        st.subheader(f"{st.session_state.symbol} {timeframe} Signals")
        
        # Price chart
        st.line_chart(
            st.session_state.df.set_index("Time")["Price"],
            use_container_width=True
        )
        
        # Signals table
        st.dataframe(
            st.session_state.df.sort_values("Time", ascending=False),
            column_config={
                "Time": st.column_config.DatetimeColumn("Time"),
                "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "Recommendation": "Signal",
                "Confidence %": st.column_config.ProgressColumn(
                    "Confidence",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100
                )
            },
            hide_index=True,
            use_container_width=True
        )

if __name__ == "__main__":
    main()
