import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import random

# Configure page
st.set_page_config(page_title="Vedic Astro Trader", layout="wide")
st.title("🌌 Vedic Astro Trading Signals")
st.markdown("### Planetary Transit & Nakshatra Analysis")

# Vedic Astrology Configuration
VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu"
}

# Nakshatra Configuration (simplified for key symbols)
NAKSHATRA_BOOST = {
    "SILVER": {"Moon": ["Rohini", "Hasta", "Shravana"], "boost": 1.2},  # Boosts bullish signals
    "GOLD": {"Sun": ["Krittika", "Uttara Phalguni"], "boost": 1.1},
    "CRUDE": {"Jupiter": ["Punarvasu", "Vishakha"], "boost": 1.1},
    "NIFTY": {"Mars": ["Mrigashira", "Dhanishta"], "boost": 1.1}
}

# Trading symbol configurations
SYMBOL_CONFIG = {
    "GOLD": {
        "planets": ["Sun", "Venus", "Saturn"],
        "colors": {"bullish": "#FFD700", "bearish": "#B8860B"},
        "rulers": {
            "Sun": {"strong": ["Trine", "Sextile"], "weak": ["Square", "Opposition"]},
            "Venus": {"strong": ["Trine", "Conjunction"], "weak": ["Square"]}
        }
    },
    "SILVER": {
        "planets": ["Moon", "Venus"],
        "colors": {"bullish": "#C0C0C0", "bearish": "#808080"},
        "rulers": {
            "Moon": {"strong": ["Trine", "Sextile"], "weak": ["Square"]}
        }
    },
    "CRUDE": {
        "planets": ["Jupiter", "Neptune"],
        "colors": {"bullish": "#FF4500", "bearish": "#8B0000"},
        "rulers": {
            "Jupiter": {"strong": ["Trine"], "weak": ["Square"]}
        }
    },
    "NIFTY": {
        "planets": ["Sun", "Mars"],
        "colors": {"bullish": "#32CD32", "bearish": "#006400"},
        "rulers": {
            "Mars": {"strong": ["Conjunction"], "weak": ["Opposition"]}
        }
    }
}

# Default user agent strings for web scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def get_random_user_agent():
    """Return a random user agent for web requests"""
    return random.choice(USER_AGENTS)

def fetch_vedic_rishi_data(date):
    """Attempt to fetch transit data from Vedic Rishi API"""
    try:
        url = "https://api.vedicrishiastro.com/v1/transit_planets"
        payload = {
            "date": date.strftime('%Y-%m-%d'),
            "timezone": "Asia/Kolkata",
            "api_key": "your_api_key"  # Replace with actual Vedic Rishi API key
        }
        headers = {"User-Agent": get_random_user_agent()}
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        transits = [
            {
                "Planet": t["planet"],
                "Time": date.strftime("%H:%M:%S"),
                "Position": f"{int(t['degree'])}°{int((t['degree'] % 1) * 60)}'{int((t['degree'] % 1) * 3600) % 60}\"",
                "Motion": "R" if t.get("retrograde", False) else "D",
                "Nakshatra": t.get("nakshatra", random.choice(["Rohini", "Hasta", "Krittika", "Punarvasu"]))
            }
            for t in data.get("transits", [])
        ]
        return transits
    except Exception as e:
        st.warning(f"Could not fetch from Vedic Rishi: {str(e)}")
        return None

def fetch_astroseek_data(date):
    """Attempt to scrape transit data from AstroSeek"""
    try:
        url = f"https://www.astro-seek.com/transit-chart?date={date.strftime('%Y-%m-%d')}&sidereal=1"
        headers = {"User-Agent": get_random_user_agent()}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        transits = []
        # Hypothetical selector; update after inspecting AstroSeek HTML
        for row in soup.select('table.transit-table tr')[1:]:
            cols = row.select('td')
            if len(cols) >= 3:
                transits.append({
                    "Planet": cols[0].text.strip(),
                    "Time": date.strftime("%H:%M:%S"),
                    "Position": cols[1].text.strip(),
                    "Motion": "R" if "Retro" in cols[2].text else "D",
                    "Nakshatra": random.choice(["Rohini", "Hasta", "Krittika", "Punarvasu"])  # Placeholder
                })
        return transits if transits else None
    except Exception as e:
        st.warning(f"Could not fetch from AstroSeek: {str(e)}")
        return None

def fetch_astronomics_data(date):
    """Fetch data from preferred sources with fallback to sample data"""
    # Try Vedic Rishi API first
    transits = fetch_vedic_rishi_data(date)
    if transits:
        return transits
    
    # Try AstroSeek as backup
    transits = fetch_astroseek_data(date)
    if transits:
        return transits
    
    # Fallback to sample data
    st.info("Using sample data (real data unavailable)")
    return generate_sample_data()

def generate_sample_data(date):
    """Generate sample data with Nakshatras when API fails"""
    planets = list(VEDIC_PLANETS.keys())
    nakshatras = ["Rohini", "Hasta", "Krittika", "Punarvasu", "Mrigashira", "Dhanishta"]
    return [{
        "Planet": random.choice(planets),
        "Time": date.strftime("%H:%M:%S"),
        "Position": f"{random.randint(0, 29)}°{random.randint(0, 59)}'{random.randint(0, 59)}\"",
        "Motion": random.choice(["D", "R"]),
        "Nakshatra": random.choice(nakshatras)
    } for _ in range(6)]

def calculate_aspect(position):
    """Calculate aspect based on zodiac position"""
    try:
        deg = float(position.split('°')[0])
        if deg % 30 < 5 or deg % 30 > 25:
            return "Conjunction"
        elif 55 < deg % 60 < 65:
            return "Sextile"
        elif 85 < deg % 90 < 95:
            return "Square"
        elif 115 < deg % 120 < 125:
            return "Trine"
        elif 175 < deg % 180 < 185:
            return "Opposition"
    except:
        pass
    return random.choice(["Conjunction", "Sextile", "Square", "Trine"])

def determine_effect(planet, aspect, rulers, motion, symbol, nakshatra):
    """Determine market effect with motion and Nakshatra consideration"""
    strength = 1.3 if motion == "R" else 1.0  # Retrograde amplification
    nakshatra_boost = 1.0
    if symbol in NAKSHATRA_BOOST and planet in NAKSHATRA_BOOST[symbol]:
        if nakshatra in NAKSHATRA_BOOST[symbol][planet]:
            nakshatra_boost = NAKSHATRA_BOOST[symbol]["boost"]
    
    if planet in rulers:
        if aspect in rulers[planet].get("strong", []):
            return "Strong Bullish", f"+{random.uniform(0.8, 1.5) * strength * nakshatra_boost:.1f}%"
        elif aspect in rulers[planet].get("weak", []):
            return "Strong Bearish", f"-{random.uniform(0.8, 1.5) * strength / nakshatra_boost:.1f}%"
    
    return random.choice(["Mild Bullish", "Mild Bearish", "Neutral"]), f"{random.uniform(-0.3, 0.3) * nakshatra_boost:.1f}%"

def get_trading_action(effect):
    """Get trading action recommendation"""
    return {
        "Strong Bullish": "STRONG BUY",
        "Mild Bullish": "BUY",
        "Neutral": "HOLD",
        "Mild Bearish": "SELL",
        "Strong Bearish": "STRONG SELL"
    }.get(effect, "HOLD")

def generate_interpretation(planet, aspect, symbol, nakshatra):
    """Generate interpretation text with Nakshatra"""
    vedic = VEDIC_PLANETS.get(planet, planet)
    base = {
        "Conjunction": f"{vedic} directly influencing {symbol}",
        "Sextile": f"Favorable energy from {vedic} for {symbol}",
        "Square": f"Challenging aspect from {vedic} on {symbol}",
        "Trine": f"Harmonious support from {vedic} for {symbol}",
        "Opposition": f"Polarized influence from {vedic} on {symbol}"
    }.get(aspect, f"{vedic} affecting {symbol} market")
    return f"{base} (Nakshatra: {nakshatra})"

def generate_signals(symbol, transits):
    """Generate trading signals from transit data"""
    config = SYMBOL_CONFIG.get(symbol, {})
    signals = []
    
    for transit in transits:
        planet = transit["Planet"]
        if planet not in config.get("planets", []):
            continue
            
        aspect = calculate_aspect(transit["Position"])
        effect, impact = determine_effect(planet, aspect, config.get("rulers", {}), transit["Motion"], symbol, transit["Nakshatra"])
        
        signals.append({
            "Time": transit["Time"][:5],
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, planet)})",
            "Aspect": aspect,
            "Nakshatra": transit["Nakshatra"],
            "Impact": impact,
            "Effect": effect,
            "Action": get_trading_action(effect),
            "Interpretation": generate_interpretation(planet, aspect, symbol, transit["Nakshatra"])
        })
    
    return signals

def main():
    """Main application function"""
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.selectbox(
            "Select Symbol",
            list(SYMBOL_CONFIG.keys()),
            index=0
        )
    with col2:
        selected_date = st.date_input(
            "Select Date",
            value=datetime.now()
        )

    if st.button("Generate Trading Signals"):
        with st.spinner("Analyzing planetary transits..."):
            # Fetch transit data with fallbacks
            transits = fetch_astronomics_data(selected_date)
            
            if not transits:
                st.warning("No transit data available")
                st.stop()
            
            signals = generate_signals(symbol, transits)
            
            if not signals:
                st.warning("No significant planetary aspects found for selected symbol")
                st.stop()
                
            # Create and display dataframe
            df = pd.DataFrame(signals).sort_values("Time")
            
            # Apply styling
            def color_effect(val):
                colors = {
                    "Strong Bullish": "#27ae60",
                    "Mild Bullish": "#2ecc71",
                    "Neutral": "#95a5a6",
                    "Mild Bearish": "#e67e22",
                    "Strong Bearish": "#e74c3c"
                }
                return f'background-color: {colors.get(val, "#95a5a6")}; color: white'
            
            def color_action(val):
                colors = {
                    "STRONG BUY": "#16a085",
                    "BUY": "#27ae60",
                    "HOLD": "#95a5a6",
                    "SELL": "#e67e22",
                    "STRONG SELL": "#c0392b"
                }
                return f'background-color: {colors.get(val, "#95a5a6")}; color: white; font-weight: bold'
            
            styled_df = df.style\
                .applymap(color_effect, subset=['Effect'])\
                .applymap(color_action, subset=['Action'])\
                .set_properties(**{'text-align': 'left'})
            
            st.dataframe(
                styled_df,
                column_config={
                    "Time": "Time",
                    "Planet": "Planet",
                    "Aspect": "Aspect",
                    "Nakshatra": "Nakshatra",
                    "Impact": "Impact",
                    "Effect": "Effect",
                    "Action": "Action",
                    "Interpretation": "Interpretation"
                },
                use_container_width=True,
                height=min(800, 45 * len(df)),
                hide_index=True
            )

if __name__ == "__main__":
    main()
