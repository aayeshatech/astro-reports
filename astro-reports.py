import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import random
import hashlib
import calendar
import plotly.graph_objects as go

# App configuration
st.set_page_config(
    page_title="Advanced Astro Trading Signals",
    layout="wide",
    initial_sidebar_state="expanded"
)

def generate_astro_transits(selected_date):
    planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    aspects = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
    
    transits = []
    for _ in range(7):
        planet = random.choice(planets)
        aspect = random.choice(aspects)
        strength = random.uniform(0.5, 1.0)
        
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
    
    for i in range(1, len(dates)):
        if i % 7 == 0:
            movements[i] += random.uniform(-0.01, 0.01)
        if dates[i].day == 15:
            movements[i] += random.uniform(-0.02, 0.02)
    
    prices = base_price * (1 + movements.cumsum())
    
    # Generate OHLC data with proper random variations
    opens = prices * (1 + np.random.normal(0, 0.001, len(dates))
    highs = prices * (1 + np.random.normal(0.002, 0.001, len(dates))
    lows = prices * (1 + np.random.normal(-0.002, 0.001, len(dates))
    
    return pd.DataFrame({
        "DateTime": dates,
        "Open": np.round(opens, 2),
        "High": np.round(highs, 2),
        "Low": np.round(lows, 2),
        "Close": np.round(prices, 2)
    })

def create_tradingview_chart(df):
    fig = go.Figure(data=[go.Candlestick(
        x=df['DateTime'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='#2ECC71',  # Green
        decreasing_line_color='#E74C3C'   # Red
    )])
    
    fig.update_layout(
        title=f'{st.session_state.symbol} Price Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        height=600,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='#1E1E1E',  # Dark background
        paper_bgcolor='#1E1E1E',
        font=dict(color='white'),
        xaxis=dict(
            gridcolor='#444',
            showgrid=True,
            type='date'
        ),
        yaxis=dict(
            gridcolor='#444',
            showgrid=True
        )
    )
    
    # Add volume-like bars at bottom
    fig.add_trace(go.Bar(
        x=df['DateTime'],
        y=df['Close'].diff().abs()*10,  # Simulated volume
        marker_color='rgba(100, 100, 100, 0.6)',
        name='Activity'
    ), secondary_y=True)
    
    fig.update_layout(barmode='relative')
    return fig

def main():
    st.title("📈 Advanced Astro Trading Analyzer")
    
    if 'symbol' not in st.session_state:
        st.session_state.symbol = "NIFTY"
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = date.today()
    
    with st.sidebar:
        st.header("Analysis Parameters")
        st.session_state.selected_date = st.date_input(
            "Select Date", 
            value=st.session_state.selected_date,
            max_value=date.today()
        )
        
        symbol_options = ["NIFTY", "AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "Custom"]
        selected_option = st.selectbox("Select Symbol", symbol_options, index=0)
        
        if selected_option == "Custom":
            custom_symbol = st.text_input("Enter Symbol", "NIFTY").strip().upper()
            if custom_symbol:
                st.session_state.symbol = custom_symbol
        else:
            st.session_state.symbol = selected_option
        
        timeframe = st.radio("Analysis Type", 
                           ["Intraday", "Weekly", "Monthly"],
                           horizontal=True)
    
    if st.session_state.selected_date:
        with st.spinner(f"Generating {timeframe} analysis for {st.session_state.symbol}..."):
            price_df = generate_price_data(
                st.session_state.symbol,
                st.session_state.selected_date,
                timeframe
            )
            
            transit_df = generate_astro_transits(st.session_state.selected_date)
            
            start_price = price_df["Close"].iloc[0]
            end_price = price_df["Close"].iloc[-1]
            change_pct = ((end_price - start_price) / start_price * 100)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Start Price", f"${start_price:,.2f}")
            with col2:
                st.metric("End Price", f"${end_price:,.2f}")
            with col3:
                st.metric("Change", f"{change_pct:.2f}%", 
                         delta_color="inverse" if change_pct < 0 else "normal")
            
            st.subheader("TradingView Style Price Chart")
            fig = create_tradingview_chart(price_df)
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Planetary Transits & Market Impact")
            
            def color_influence(val):
                color = '#2ECC71' if "Bullish" in val else ('#E74C3C' if "Bearish" in val else '#95A5A6')
                return f'color: {color}; font-weight: bold'
            
            styled_df = transit_df.style.applymap(color_influence, subset=['Influence'])
            
            st.dataframe(
                styled_df,
                column_config={
                    "Planet": "Planet",
                    "Aspect": "Aspect",
                    "Strength": st.column_config.NumberColumn("Strength", format="%.1f"),
                    "Influence": "Market Influence",
                    "Impact": "Position",
                    "Change %": "Expected Change"
                },
                use_container_width=True,
                height=400
            )

if __name__ == "__main__":
    main()
