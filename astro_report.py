import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# App configuration
st.set_page_config(
    page_title="Astro Trading Signals",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if 'data' not in st.session_state:
    st.session_state.data = None

# Main app function
def main():
    st.title("📈 Astro Trading Signals")
    st.markdown("Analyze market trends through planetary positions")
    
    with st.sidebar:
        st.header("Parameters")
        symbol = st.selectbox("Select Symbol", ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"])
        timeframe = st.selectbox("Timeframe", ["Daily", "Weekly", "Monthly"])
        
        if st.button("Generate Signals"):
            with st.spinner("Calculating astro signals..."):
                # Generate sample data
                dates = pd.date_range(end=datetime.today(), periods=30)
                prices = np.random.normal(100, 10, 30).cumsum()
                signals = np.random.choice(["Strong Buy", "Buy", "Neutral", "Sell", "Strong Sell"], 30)
                
                st.session_state.data = pd.DataFrame({
                    "Date": dates,
                    "Price": prices,
                    "Signal": signals,
                    "Confidence": np.random.uniform(50, 95, 30).round(1)
                })
    
    # Display results
    if st.session_state.data is not None:
        st.subheader(f"Analysis for {symbol} ({timeframe})")
        
        # Price chart
        st.line_chart(st.session_state.data.set_index("Date")["Price"])
        
        # Latest signals
        st.dataframe(
            st.session_state.data.sort_values("Date", ascending=False).head(10),
            column_config={
                "Date": "Date",
                "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "Signal": "Recommendation",
                "Confidence": st.column_config.ProgressColumn(
                    "Confidence %",
                    format="%.1f",
                    min_value=0,
                    max_value=100
                )
            },
            hide_index=True,
            use_container_width=True
        )

if __name__ == "__main__":
    main()
