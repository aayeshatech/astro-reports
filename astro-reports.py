import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import random
import hashlib
import calendar
import plotly.graph_objects as go

# Try to import yfinance with fallback
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# App configuration
st.set_page_config(
    page_title="Advanced Astro Trading Signals",
    layout="wide",
    initial_sidebar_state="expanded"
)

def generate_intraday_transits(selected_date):
    planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    aspects = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
    
    transits = []
    for _ in range(24):  # Generate 24 intraday transits
        hour = random.randint(5, 23)  # From 5AM to 11PM
        minute = random.choice([0, 15, 30, 45])
        transit_time = datetime(selected_date.year, selected_date.month, selected_date.day, hour, minute)
        
        planet = random.choice(planets)
        aspect = random.choice(aspects)
        strength = random.uniform(0.5, 1.0)
        
        if planet in ["Jupiter", "Venus"]:
            if aspect in ["Trine", "Sextile"]:
                influence = "Strong Bullish"
                action = "GO LONG"
            else:
                influence = "Mildly Bullish"
                action = "CONSIDER LONG"
        elif planet in ["Saturn", "Mars"]:
            if aspect in ["Square", "Opposition"]:
                influence = "Strong Bearish"
                action = "GO SHORT"
            else:
                influence = "Mildly Bearish"
                action = "CONSIDER SHORT"
        else:
            influence = "Neutral"
            action = "HOLD"
        
        transits.append({
            "Time": transit_time.strftime("%H:%M"),
            "Planet": planet,
            "Aspect": aspect.replace("Tribe", "Trine").replace("Smith", "Square"),
            "Strength": f"{strength:.1f}",
            "Market Influence": influence,
            "Trading Action": action,
            "Effect Duration": random.choice([15, 30, 45, 60]),
            "Expected Impact": f"{random.uniform(0.1, 1.5):.1f}%"
        })
    
    return pd.DataFrame(transits).sort_values("Time").reset_index(drop=True)

def generate_astro_transits(selected_date, timeframe):
    planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    aspects = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
    
    transits = []
    days = 7 if timeframe == "Weekly" else calendar.monthrange(selected_date.year, selected_date.month)[1]
    
    for day in range(days):
        transit_date = selected_date + timedelta(days=day) if timeframe == "Weekly" else \
                     date(selected_date.year, selected_date.month, day+1)
        
        planet = random.choice(planets)
        aspect = random.choice(aspects)
        strength = random.uniform(0.5, 1.0)
        
        if planet in ["Jupiter", "Venus"]:
            if aspect in ["Trine", "Sextile"]:
                influence = "Strong Bullish"
                action = "GO LONG"
            else:
                influence = "Mildly Bullish"
                action = "CONSIDER LONG"
        elif planet in ["Saturn", "Mars"]:
            if aspect in ["Square", "Opposition"]:
                influence = "Strong Bearish"
                action = "GO SHORT"
            else:
                influence = "Mildly Bearish"
                action = "CONSIDER SHORT"
        else:
            influence = "Neutral"
            action = "HOLD"
        
        transits.append({
            "Date": transit_date.strftime("%Y-%m-%d"),
            "Planet": planet,
            "Aspect": aspect.replace("Tribe", "Trine").replace("Smith", "Square"),
            "Strength": f"{strength:.1f}",
            "Market Influence": influence,
            "Trading Action": action,
            "Expected Impact": f"{random.uniform(0.5, 5.0):.1f}%"
        })
    
    return pd.DataFrame(transits)

def generate_price_data(symbol, start_date, timeframe):
    if YFINANCE_AVAILABLE:
        if symbol in ["GOLD", "GC", "XAU"]:
            ticker = "GC=F"
        elif symbol in ["SILVER", "SI", "XAG"]:
            ticker = "SI=F"
        else:
            ticker = symbol
        
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="1d")
            base_price = hist["Close"].iloc[-1]
        except:
            base_price = None
    
    if not YFINANCE_AVAILABLE or base_price is None:
        base_price = {
            "AAPL": 180, "MSFT": 300, "GOOG": 140, 
            "AMZN": 120, "TSLA": 200, "NIFTY": 18000,
            "GOLD": 3305, "GC": 3305, "XAU": 3305,
            "SILVER": 28.50, "SI": 28.50, "XAG": 28.50
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
    prices = base_price * (1 + movements.cumsum())
    
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

def create_tradingview_chart(df):
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=df['DateTime'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='#2ECC71',
        decreasing_line_color='#E74C3C',
        name='Price'
    ))
    
    fig.add_trace(go.Bar(
        x=df['DateTime'],
        y=df['Volume'],
        marker_color='rgba(100, 100, 100, 0.6)',
        name='Volume',
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=f'{st.session_state.symbol} Price Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        height=600,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#1E1E1E',
        font=dict(color='white'),
        xaxis=dict(
            gridcolor='#444',
            showgrid=True,
            type='date',
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            gridcolor='#444',
            showgrid=True,
            domain=[0.2, 1]
        ),
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right',
            showgrid=False,
            domain=[0, 0.18]
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
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
        
        symbol_options = ["NIFTY", "AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "GOLD", "SILVER", "Custom"]
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
            
            if timeframe == "Intraday":
                transit_df = generate_intraday_transits(st.session_state.selected_date)
            else:
                transit_df = generate_astro_transits(st.session_state.selected_date, timeframe)
            
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
                colors = {
                    "Strong Bullish": "#27AE60",
                    "Mildly Bullish": "#58D68D",
                    "Neutral": "#95A5A6",
                    "Mildly Bearish": "#EC7063",
                    "Strong Bearish": "#C0392B"
                }
                return f'background-color: {colors.get(val, "#95A5A6")}; color: white'
            
            def color_action(val):
                colors = {
                    "GO LONG": "#27AE60",
                    "CONSIDER LONG": "#2ECC71",
                    "HOLD": "#95A5A6",
                    "CONSIDER SHORT": "#E74C3C",
                    "GO SHORT": "#C0392B"
                }
                return f'background-color: {colors.get(val, "#95A5A6")}; color: white; font-weight: bold'
            
            if timeframe == "Intraday":
                columns = {
                    "Time": "Transit Time",
                    "Planet": "Planet",
                    "Aspect": "Aspect",
                    "Strength": "Strength",
                    "Market Influence": "Market Influence",
                    "Trading Action": "Trading Action",
                    "Effect Duration": "Duration (min)",
                    "Expected Impact": "Expected Impact"
                }
                height = 800
            else:
                columns = {
                    "Date": "Transit Date",
                    "Planet": "Planet",
                    "Aspect": "Aspect",
                    "Strength": "Strength",
                    "Market Influence": "Market Influence",
                    "Trading Action": "Trading Action",
                    "Expected Impact": "Expected Impact"
                }
                height = 600
            
            styled_df = transit_df.style\
                .applymap(color_influence, subset=['Market Influence'])\
                .applymap(color_action, subset=['Trading Action'])\
                .set_properties(**{'text-align': 'center'})
            
            st.dataframe(
                styled_df,
                column_config=columns,
                use_container_width=True,
                height=height
            )

if __name__ == "__main__":
    main()
