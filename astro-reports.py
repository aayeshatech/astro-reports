import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import random

# Vedic Astrology Configuration
VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu"
}

# Planetary effects for different symbols
SYMBOL_RULERSHIPS = {
    "GOLD": {
        "Sun": {"strong": ["Trine", "Sextile"], "weak": ["Square", "Opposition"]},
        "Venus": {"strong": ["Trine", "Conjunction"], "weak": ["Square"]},
        "Saturn": {"strong": [], "weak": ["Conjunction", "Opposition"]}
    },
    "SILVER": {
        "Moon": {"strong": ["Trine", "Sextile"], "weak": ["Square"]},
        "Venus": {"strong": ["Conjunction"], "weak": ["Opposition"]}
    },
    "CRUDE": {
        "Jupiter": {"strong": ["Trine"], "weak": ["Square"]},
        "Neptune": {"strong": ["Sextile"], "weak": ["Opposition"]}
    },
    "NIFTY": {
        "Sun": {"strong": ["Trine"], "weak": ["Square"]},
        "Mars": {"strong": ["Conjunction"], "weak": ["Opposition"]}
    }
}

def generate_transits(symbol, start_date, timeframe):
    """Generate astrological transits for different timeframes"""
    aspects = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
    transits = []
    
    # Get rulerships for the selected symbol or use default
    planetary_effects = SYMBOL_RULERSHIPS.get(symbol, {})
    
    if timeframe == "Intraday":
        # Generate intraday transits from 5 AM to 11:45 PM in 30-min intervals
        for hour in range(5, 24):  # 5 AM to 11 PM
            for minute in [0, 30]:  # Every 30 minutes
                if hour == 23 and minute == 30:  # Skip 11:30 PM
                    continue
                
                planet = random.choice(list(VEDIC_PLANETS.keys()))
                aspect = random.choice(aspects)
                
                effect, impact = determine_effect(planet, aspect, planetary_effects)
                interpretation = generate_interpretation(planet, aspect, symbol)
                
                transits.append({
                    "Time": f"{hour:02d}:{minute:02d}",
                    "Planet": f"{planet} ({VEDIC_PLANETS[planet]})",
                    "Aspect": aspect,
                    "Impact": impact,
                    "Effect": effect,
                    "Action": get_action(effect),
                    "Interpretation": interpretation
                })
    else:
        days = 7 if timeframe == "Weekly" else 30
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            planet = random.choice(list(VEDIC_PLANETS.keys()))
            aspect = random.choice(aspects)
            
            effect, impact = determine_effect(planet, aspect, planetary_effects)
            interpretation = generate_interpretation(planet, aspect, symbol)
            
            transits.append({
                "Date": current_date.strftime("%b %-d"),
                "Planet": f"{planet} ({VEDIC_PLANETS[planet]})",
                "Aspect": aspect,
                "Impact": impact,
                "Effect": effect,
                "Action": get_action(effect),
                "Interpretation": interpretation
            })
    
    return pd.DataFrame(transits)

def determine_effect(planet, aspect, planetary_effects):
    """Determine market effect based on planetary aspects"""
    if planet in planetary_effects:
        if aspect in planetary_effects[planet]["strong"]:
            effect = "Strong Bullish"
            impact = f"+{random.uniform(0.8, 2.0):.1f}%"
        elif aspect in planetary_effects[planet]["weak"]:
            effect = "Strong Bearish"
            impact = f"-{random.uniform(0.8, 2.0):.1f}%"
        else:
            effect = "Neutral"
            impact = f"{random.uniform(-0.5, 0.5):.1f}%"
    else:
        effect = "Mild Bullish" if random.random() > 0.5 else "Mild Bearish"
        impact = f"{random.uniform(-0.7, 0.7):.1f}%"
    return effect, impact

def get_action(effect):
    """Determine trading action based on effect"""
    if "Strong Bullish" in effect:
        return "GO LONG"
    elif "Mild Bullish" in effect:
        return "Consider LONG"
    elif "Strong Bearish" in effect:
        return "GO SHORT"
    elif "Mild Bearish" in effect:
        return "Consider SHORT"
    return "HOLD"

def generate_interpretation(planet, aspect, symbol):
    """Generate interpretation for any symbol"""
    vedic_name = VEDIC_PLANETS[planet]
    action_words = {
        "Conjunction": "influencing",
        "Sextile": "supporting",
        "Square": "pressuring",
        "Trine": "benefiting",
        "Opposition": "challenging"
    }
    return f"{vedic_name}'s {aspect.lower()} {action_words[aspect]} {symbol.lower()} market"

# Streamlit App
def main():
    st.title("Vedic Astro Trading Signals")
    
    # Symbol input section
    st.subheader("Symbol Selection")
    symbol = st.text_input("Enter Symbol (e.g., GOLD, BTC, NIFTY)", "GOLD").strip().upper()
    
    # Timeframe selection
    st.subheader("Analysis Parameters")
    col1, col2 = st.columns(2)
    with col1:
        timeframe = st.selectbox("Timeframe", ["Intraday", "Weekly", "Monthly"], index=0)
    with col2:
        start_date = st.date_input("Start Date", value=datetime.today())
    
    if st.button("Generate Astro Trading Report"):
        if not symbol:
            st.warning("Please enter a symbol")
            return
            
        with st.spinner(f"Generating {timeframe} Vedic astrology report for {symbol}..."):
            transit_df = generate_transits(symbol, start_date, timeframe)
            
            # Apply styling
            def color_effect(val):
                colors = {
                    "Strong Bullish": "#27AE60",
                    "Mild Bullish": "#58D68D",
                    "Neutral": "#95A5A6",
                    "Mild Bearish": "#E74C3C",
                    "Strong Bearish": "#C0392B"
                }
                return f'background-color: {colors.get(val, "#95A5A6")}; color: white'
            
            def color_action(val):
                colors = {
                    "GO LONG": "#27AE60",
                    "Consider LONG": "#2ECC71",
                    "HOLD": "#95A5A6",
                    "Consider SHORT": "#E74C3C",
                    "GO SHORT": "#C0392B"
                }
                return f'background-color: {colors.get(val, "#95A5A6")}; color: white; font-weight: bold'
            
            styled_df = transit_df.style\
                .applymap(color_effect, subset=['Effect'])\
                .applymap(color_action, subset=['Action'])\
                .set_properties(**{'text-align': 'left'})
            
            # Display appropriate columns based on timeframe
            if timeframe == "Intraday":
                columns = {
                    "Time": "Time (24h)",
                    "Planet": "Planet (Vedic)",
                    "Aspect": "Aspect",
                    "Impact": "Price Impact",
                    "Effect": "Market Effect",
                    "Action": "Trading Action",
                    "Interpretation": "Astro Interpretation"
                }
                height = min(800, 35 * len(transit_df))  # Dynamic height
            else:
                columns = {
                    "Date": "Date",
                    "Planet": "Planet (Vedic)",
                    "Aspect": "Aspect",
                    "Impact": "Price Impact",
                    "Effect": "Market Effect",
                    "Action": "Trading Action",
                    "Interpretation": "Astro Interpretation"
                }
                height = min(800, 35 * len(transit_df))
            
            st.dataframe(
                styled_df,
                column_config=columns,
                use_container_width=True,
                height=height,
                hide_index=True
            )

if __name__ == "__main__":
    main() 
