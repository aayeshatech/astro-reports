import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# Vedic Astrology Configuration
VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu"
}

def generate_vedic_transits(symbol, start_date, days=15):
    """Generate Vedic astrological transits for the specified symbol"""
    aspects = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
    transits = []
    
    # Gold-specific rulerships
    if symbol == "GOLD":
        planetary_effects = {
            "Sun": {"strong": ["Trine", "Sextile"], "weak": ["Square", "Opposition"]},
            "Venus": {"strong": ["Trine", "Conjunction"], "weak": ["Square"]},
            "Saturn": {"strong": [], "weak": ["Conjunction", "Opposition"]}
        }
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        planet = random.choice(list(VEDIC_PLANETS.keys()))
        aspect = random.choice(aspects)
        
        # Determine market effect based on Vedic rules
        effect = ""
        impact = 0
        if symbol == "GOLD":
            if planet in planetary_effects:
                if aspect in planetary_effects[planet]["strong"]:
                    effect = "Strong Bullish"
                    impact = round(random.uniform(0.8, 2.0), 1)
                elif aspect in planetary_effects[planet]["weak"]:
                    effect = "Strong Bearish"
                    impact = round(random.uniform(-2.0, -0.8), 1)
                else:
                    effect = "Neutral"
                    impact = round(random.uniform(-0.5, 0.5), 1)
            else:
                effect = "Mild Bullish" if random.random() > 0.5 else "Mild Bearish"
                impact = round(random.uniform(-0.7, 0.7), 1)
        
        # Generate interpretation note
        notes = {
            "Conjunction": f"{VEDIC_PLANETS[planet]} conjunction →",
            "Sextile": f"{VEDIC_PLANETS[planet]} sextile supports",
            "Square": f"{VEDIC_PLANETS[planet]} square pressures",
            "Trine": f"{VEDIC_PLANETS[planet]} trine benefits",
            "Opposition": f"{VEDIC_PLANETS[planet]} opposes"
        }[aspect]
        
        transits.append({
            "Date": current_date.strftime("%b %-d"),
            "Planet": planet,
            "Aspect": aspect,
            "Impact": f"{'+' if impact >=0 else ''}{impact}%",
            "Effect": effect,
            "Interpretation": f"{notes} {symbol.lower()}"
        })
    
    return pd.DataFrame(transits)

# Streamlit App
def main():
    st.title("Vedic Astro Trading Signals")
    
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.selectbox("Select Symbol", ["GOLD", "SILVER", "CRUDE", "NIFTY"], index=0)
    with col2:
        start_date = st.date_input("Start Date", value=datetime.today())
    
    days = st.slider("Forecast Period (days)", 7, 30, 15)
    
    if st.button("Generate Astro Report"):
        transit_df = generate_vedic_transits(symbol, start_date, days)
        
        # Apply styling
        def color_effect(val):
            color = {
                "Strong Bullish": "#27AE60",
                "Mild Bullish": "#58D68D",
                "Neutral": "#95A5A6",
                "Mild Bearish": "#E74C3C",
                "Strong Bearish": "#C0392B"
            }.get(val, "#95A5A6")
            return f'background-color: {color}; color: white'
        
        styled_df = transit_df.style\
            .applymap(color_effect, subset=['Effect'])\
            .set_properties(**{'text-align': 'left'})
        
        st.dataframe(
            styled_df,
            column_config={
                "Date": "Date",
                "Planet": "Planet (Vedic)",
                "Aspect": "Aspect",
                "Impact": "Price Impact",
                "Effect": "Market Effect",
                "Interpretation": "Astrological Interpretation"
            },
            use_container_width=True,
            height=800,
            hide_index=True
        )

if __name__ == "__main__":
    main()
