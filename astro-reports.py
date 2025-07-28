import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import random
import hashlib
import calendar

# App configuration
st.set_page_config(
    page_title="Advanced Astro Trading Signals",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Generate planetary transits with bullish/bearish indicators
def generate_astro_transits(selected_date):
    planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    aspects = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
    
    transits = []
    for _ in range(7):  # Generate 7 transits for the selected period
        planet = random.choice(planets)
        aspect = random.choice(aspects)
        strength = random.uniform(0.5, 1.0)
        
        # Determine influence
        if planet in ["Jupiter", "Venus"]:
            influence = "Bullish" if aspect in ["Trine", "Sextile"] else "Mildly Bullish"
        elif planet in ["Saturn", "Mars"]:
            influence = "Bearish" if aspect in ["Square", "Opposition"] else "Mildly Bearish"
        else:
            influence = "Neutral"
        
        transits.append({
            "Planet": planet,
            "Aspect": aspect,
            "Strength": f"{strength:.1f}",
            "Influence": influence,
            "Impact": random.choice(["Long", "Short"]),
            "Change %": f"{random.uniform(0.5, 5.0):.1f}%"
        })
    
    return pd.DataFrame(transits)

# Generate price data with astro influence
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
    
    return pd.DataFrame({
        "DateTime": dates,
        "Price": prices.round(2),
        "EMA_20": prices.ewm(span=20).mean().round(2),
        "EMA_50": prices.ewm(span=50).mean().round(2)
    })

# Main app
def main():
    st.title("📈 Advanced Astro Trading Analyzer")
    
    # Initialize session state
    if 'symbol' not in st.session_state:
        st.session_state.symbol = "NIFTY"
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = date.today()
    
    with st.sidebar:
        st.header("Analysis Parameters")
        
        # Date selection
        st.session_state.selected_date = st.date_input(
            "Select Date", 
            value=st.session_state.selected_date,
            max_value=date.today()
        )
        
        # Symbol selection
        symbol_options = ["NIFTY", "AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "Custom"]
        selected_option = st.selectbox("Select Symbol", symbol_options, index=0)
        
        if selected_option == "Custom":
            custom_symbol = st.text_input("Enter Symbol", "NIFTY").strip().upper()
            if custom_symbol:
                st.session_state.symbol = custom_symbol
        else:
            st.session_state.symbol = selected_option
        
        # Timeframe selection
        timeframe = st.radio("Analysis Type", 
                           ["Intraday", "Weekly", "Monthly"],
                           horizontal=True)
    
    # Generate data when date changes
    if st.session_state.selected_date:
        with st.spinner(f"Generating {timeframe} analysis for {st.session_state.symbol}..."):
            # Generate price data
            price_df = generate_price_data(
                st.session_state.symbol,
                st.session_state.selected_date,
                timeframe
            )
            
            # Generate astro transits
            transit_df = generate_astro_transits(st.session_state.selected_date)
            
            # Calculate summary stats
            start_price = price_df["Price"].iloc[0]
            end_price = price_df["Price"].iloc[-1]
            change_pct = ((end_price - start_price) / start_price * 100)
            
            # Display summary cards
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Start Price", f"${start_price:,.2f}")
            with col2:
                st.metric("End Price", f"${end_price:,.2f}")
            with col3:
                st.metric("Change", f"{change_pct:.2f}%", 
                         delta_color="inverse" if change_pct < 0 else "normal")
            
            # Price chart with Streamlit native charts
            st.subheader("Price Movement")
            st.line_chart(
                price_df.set_index("DateTime")[["Price", "EMA_20", "EMA_50"]],
                use_container_width=True
            )
            
            # Daily changes
            st.subheader("Daily Percentage Changes")
            st.bar_chart(
                price_df.set_index("DateTime")["Price"].pct_change()*100,
                use_container_width=True
            )
            
            # Show astro transits
            st.subheader("Planetary Transits & Market Impact")
            
            # Color formatting for transits
            def color_influence(val):
                color = 'green' if "Bullish" in val else ('red' if "Bearish" in val else 'gray')
                return f'color: {color}'
            
            styled_df = transit_df.style.applymap(color_influence, subset=['Influence'])
            
            st.dataframe(
                styled_df,
                column_config={
                    "Planet": "Planet",
                    "Aspect": "Aspect",
                    "Strength": "Strength",
                    "Influence": "Market Influence",
                    "Impact": "Position",
                    "Change %": "Expected Change"
                },
                use_container_width=True,
                height=400
            )

if __name__ == "__main__":
    main()
