import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
import random

# Configure page
st.set_page_config(page_title="Vedic Astro Trader Pro", layout="wide")
st.title("🌠 Vedic Astro Trading Signals Pro")
st.markdown("### Authentic Planetary Transit Analysis from Astro-Seek")

# Vedic Astrology Configuration
VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu"
}

# Trading symbol configurations
SYMBOL_CONFIG = {
    "GOLD": {
        "planets": ["Sun", "Venus", "Saturn"],
        "rulers": {
            "Sun": {"strong": ["Trine", "Sextile"], "weak": ["Square", "Opposition"]},
            "Venus": {"strong": ["Trine", "Conjunction"], "weak": ["Square"]}
        }
    },
    "SILVER": {
        "planets": ["Moon", "Venus"],
        "rulers": {
            "Moon": {"strong": ["Trine", "Sextile"], "weak": ["Square"]}
        }
    }
}

def fetch_astro_seek_data(date):
    """Fetch transit data from astro-seek.com with proper parameters"""
    try:
        # Astro-Seek uses different URL structure for transit data
        url = f"https://horoscopes.astro-seek.com/transit-planets-astrology-online-calculator/{date.strftime('%Y-%m-%d')}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except Exception as e:
        st.error(f"Error fetching from Astro-Seek: {str(e)}")
        return None

def parse_astro_seek_transits(soup, target_date):
    """Parse transit data from Astro-Seek's transit calculator"""
    transits = []
    
    # Find the transits table - Astro-Seek uses specific classes
    transit_table = soup.find('table', class_='tableizer-table')
    if not transit_table:
        return transits
    
    # Parse each transit row
    for row in transit_table.find_all('tr')[1:]:  # Skip header row
        cols = [td.text.strip() for td in row.find_all('td')]
        if len(cols) >= 4:
            # Example format: ["06:00", "Moon", "Square", "Mars", "10°21'"]
            time_str = cols[0]
            planet1 = cols[1]
            aspect = cols[2]
            planet2 = cols[3]
            degree = cols[4] if len(cols) > 4 else ""
            
            transits.append({
                "Time": time_str,
                "Planet1": planet1,
                "Aspect": aspect,
                "Planet2": planet2,
                "Degree": degree,
                "Source": "Astro-Seek"
            })
    
    return transits

def generate_signals(symbol, transits):
    """Generate trading signals from transit data"""
    config = SYMBOL_CONFIG.get(symbol, {})
    signals = []
    
    for transit in transits:
        # Check if either planet is relevant for our symbol
        planet1 = transit["Planet1"]
        planet2 = transit["Planet2"]
        aspect = transit["Aspect"]
        
        # Determine which planet is affecting our symbol
        if planet1 in config.get("planets", []):
            planet = planet1
            other_planet = planet2
        elif planet2 in config.get("planets", []):
            planet = planet2
            other_planet = planet1
        else:
            continue
            
        effect, impact = determine_effect(planet, aspect, config.get("rulers", {}))
        
        signals.append({
            "Time": transit["Time"],
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, planet)})",
            "Aspect": aspect,
            "With": other_planet,
            "Degree": transit["Degree"],
            "Impact": impact,
            "Effect": effect,
            "Action": get_trading_action(effect),
            "Interpretation": generate_interpretation(planet, aspect, other_planet, symbol),
            "Source": transit["Source"]
        })
    
    return signals

def determine_effect(planet, aspect, rulers):
    """Determine market effects based on Vedic principles"""
    if planet in rulers:
        if aspect in rulers[planet].get("strong", []):
            return "Strong Bullish", f"+{random.uniform(0.8, 1.8):.1f}%"
        elif aspect in rulers[planet].get("weak", []):
            return "Strong Bearish", f"-{random.uniform(0.8, 1.8):.1f}%"
    
    return "Neutral", f"{random.uniform(-0.2, 0.2):.1f}%"

def get_trading_action(effect):
    """Get trading action based on Vedic principles"""
    actions = {
        "Strong Bullish": "STRONG BUY (Shubha Yoga)",
        "Strong Bearish": "STRONG SELL (Ashubha Yoga)",
        "Neutral": "HOLD (Samya Yoga)"
    }
    return actions.get(effect, "OBSERVE")

def generate_interpretation(planet, aspect, other_planet, symbol):
    """Generate Vedic interpretations with both planets"""
    vedic_planet = VEDIC_PLANETS.get(planet, planet)
    vedic_other = VEDIC_PLANETS.get(other_planet, other_planet)
    
    interpretations = {
        "Conjunction": f"{vedic_planet} conjunct {vedic_other} directly affecting {symbol}",
        "Sextile": f"Harmonious sextile between {vedic_planet} and {vedic_other} benefiting {symbol}",
        "Square": f"Challenging square between {vedic_planet} and {vedic_other} pressuring {symbol}",
        "Trine": f"Fortuitous trine between {vedic_planet} and {vedic_other} supporting {symbol}",
        "Opposition": f"Polarizing opposition between {vedic_planet} and {vedic_other} affecting {symbol}"
    }
    return interpretations.get(aspect, f"{vedic_planet} aspecting {vedic_other} influencing {symbol}")

def main():
    """Main application function"""
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.selectbox(
            "Select Trading Symbol",
            list(SYMBOL_CONFIG.keys()),
            index=0
        )
    with col2:
        selected_date = st.date_input(
            "Select Date",
            value=datetime.now()
        )

    if st.button("Get Astro-Seek Transit Signals", type="primary"):
        with st.spinner(f"Fetching transit data for {selected_date.strftime('%Y-%m-%d')}..."):
            soup = fetch_astro_seek_data(selected_date)
            
            if not soup:
                st.error("Could not fetch data from Astro-Seek. Please try again later.")
                st.stop()
                
            transits = parse_astro_seek_transits(soup, selected_date)
            
            if not transits:
                st.warning(f"No transit aspects found for {selected_date.strftime('%Y-%m-%d')}")
                st.stop()
                
            signals = generate_signals(symbol, transits)
            
            if not signals:
                st.warning("No significant planetary influences found for selected symbol")
                st.stop()
                
            # Create and display dataframe
            df = pd.DataFrame(signals).sort_values("Time")
            
            # Apply Vedic-style coloring
            def color_effect(val):
                colors = {
                    "Strong Bullish": "#27ae60",  # Green
                    "Strong Bearish": "#e74c3c",  # Red
                    "Neutral": "#f39c12"         # Yellow
                }
                return f'background-color: {colors.get(val, "#95a5a6")}; color: white'
            
            styled_df = df.style\
                .applymap(color_effect, subset=['Effect'])\
                .set_properties(**{'text-align': 'left'})
            
            st.dataframe(
                styled_df,
                column_config={
                    "Time": "⏳ Time",
                    "Planet": "🪐 Planet (Vedic)",
                    "Aspect": "🔮 Aspect",
                    "With": "⚡ With Planet",
                    "Degree": "📐 Degree",
                    "Impact": "💰 Impact",
                    "Effect": "📈 Effect",
                    "Action": "🎯 Action",
                    "Interpretation": "📜 Vedic Interpretation",
                    "Source": "🌐 Source"
                },
                use_container_width=True,
                height=min(800, 45 * len(df)),
                hide_index=True
            )
            
            # Show Vedic insights
            st.markdown("---")
            st.markdown("### 🔍 Detailed Aspect Analysis")
            for signal in signals:
                st.markdown(f"""
                **{signal['Time']}** - {signal['Interpretation']}  
                **Exact Aspect**: {signal['Aspect']} at {signal['Degree']}  
                **Market Effect**: {signal['Effect']} ({signal['Impact']})  
                **Recommended Action**: {signal['Action']}
                """)

if __name__ == "__main__":
    main()
