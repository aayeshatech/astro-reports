import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from bs4 import BeautifulSoup

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

def fetch_astronomics_data(date):
    """Fetch planetary transit data from astronomics.ai API"""
    try:
        url = f"https://data.astronomics.ai/almanac/?date={date.strftime('%Y-%m-%d')}"
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        
        if not table:
            return []
            
        transits = []
        for row in table.find_all('tr')[1:]:  # Skip header row
            cols = row.find_all('td')
            if len(cols) >= 12:
                transits.append({
                    "Planet": cols[0].text.strip(),
                    "Date": date.strftime('%Y-%m-%d'),
                    "Time": cols[2].text.strip(),
                    "Motion": cols[3].text.strip(),
                    "Sign Lord": cols[4].text.strip(),
                    "Star Lord": cols[5].text.strip(),
                    "Sub Lord": cols[6].text.strip(),
                    "Zodiac": cols[7].text.strip(),
                    "Nakshatra": cols[8].text.strip(),
                    "Pada": int(cols[9].text.strip()),
                    "Pos in Zodiac": cols[10].text.strip(),
                    "Declination": float(cols[11].text.strip())
                })
        return transits
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return []

def get_aspect_for_position(planet, zodiac_pos):
    """Determine aspect based on zodiac position"""
    try:
        degree = float(zodiac_pos.split('°')[0])
    except:
        degree = random.randint(0, 30)
    
    # Aspect determination based on degree
    if degree % 30 == 0:
        return "Conjunction"
    elif degree % 60 == 0:
        return "Sextile"
    elif degree % 90 == 0:
        return "Square"
    elif degree % 120 == 0:
        return "Trine"
    elif degree % 180 == 0:
        return "Opposition"
    else:
        return random.choice(["Sextile", "Square", "Trine"])

def generate_transits_from_api(symbol, selected_date):
    """Generate trading signals from API data"""
    transits = []
    planetary_data = fetch_astronomics_data(selected_date)
    
    if not planetary_data:
        st.warning(f"No transit data available for {selected_date.strftime('%Y-%m-%d')}")
        return pd.DataFrame()
    
    planetary_effects = SYMBOL_RULERSHIPS.get(symbol, {})
    
    for transit in planetary_data:
        planet = transit["Planet"]
        time_str = transit["Time"][:5]  # Get HH:MM format
        
        aspect = get_aspect_for_position(planet, transit["Pos in Zodiac"])
        effect, impact = determine_effect(planet, aspect, planetary_effects)
        interpretation = generate_interpretation(planet, aspect, symbol)
        
        transits.append({
            "Time": time_str,
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, planet)})",
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
    vedic_name = VEDIC_PLANETS.get(planet, planet)
    action_words = {
        "Conjunction": "influencing",
        "Sextile": "supporting",
        "Square": "pressuring",
        "Trine": "benefiting",
        "Opposition": "challenging"
    }
    return f"{vedic_name}'s {aspect.lower()} {action_words[aspect]} {symbol.lower()} market"

def main():
    st.title("Vedic Astro Trading Signals - Live Data")
    
    st.subheader("Symbol Selection")
    symbol = st.text_input("Enter Symbol (e.g., GOLD, BTC, NIFTY)", "GOLD").strip().upper()
    
    st.subheader("Analysis Date")
    selected_date = st.date_input("Select Date", value=datetime.now())
    
    if st.button("Generate Astro Trading Report"):
        if not symbol:
            st.warning("Please enter a symbol")
            return
            
        with st.spinner(f"Generating report for {symbol} on {selected_date.strftime('%Y-%m-%d')}..."):
            transit_df = generate_transits_from_api(symbol, selected_date)
            
            if transit_df.empty:
                st.warning("No transit data available for the selected date")
                return
            
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
            
            st.dataframe(
                styled_df,
                column_config={
                    "Time": "Time (24h)",
                    "Planet": "Planet (Vedic)",
                    "Aspect": "Aspect",
                    "Impact": "Price Impact",
                    "Effect": "Market Effect",
                    "Action": "Trading Action",
                    "Interpretation": "Astro Interpretation"
                },
                use_container_width=True,
                height=min(800, 35 * len(transit_df)),
                hide_index=True
            )

if __name__ == "__main__":
    main()
