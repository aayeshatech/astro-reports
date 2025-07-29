import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup
import random
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(page_title="Vedic Astro Trader", layout="wide")
st.title("🌌 Vedic Astro Trading Signals")
st.markdown("### Planetary Transit & Nakshatra Analysis for the Day")

# Vedic Astrology Configuration
VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu"
}

# Nakshatra Configuration
NAKSHATRA_BOOST = {
    "SILVER": {"Moon": ["Rohini", "Hasta", "Shravana"], "boost": 1.2},
    "GOLD": {"Sun": ["Krittika", "Uttara Phalguni"], "boost": 1.1},
    "CRUDE": {"Jupiter": ["Punarvasu", "Vishakha"], "boost": 1.1},
    "NIFTY": {"Mars": ["Mrigashira", "Dhanishta"], "boost": 1.1}
}

# Trading symbol configurations (used only for effects, not filtering)
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

# Default user agent strings
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def get_random_user_agent():
    """Return a random user agent for web requests"""
    return random.choice(USER_AGENTS)

def utc_to_ist(utc_time_str):
    """Convert UTC time to IST (UTC+5:30)"""
    utc_time = datetime.strptime(utc_time_str, "%H:%M")
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%H:%M")

def fetch_astro_seek_data(date):
    """Attempt to scrape transit data from Astro-Seek"""
    try:
        # Adjust URL for the specific month (e.g., July 2025)
        url = f"https://horoscopes.astro-seek.com/calculate-astrology-aspects-transits-online-calendar-july-2025/?&barva=p&"
        headers = {"User-Agent": get_random_user_agent()}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        transits = []
        # Target the table rows (adjust selector based on actual HTML)
        for row in soup.select('table tr')[1:]:  # Skip header row
            cols = row.select('td')
            if len(cols) >= 3:
                date_str = cols[0].text.strip()
                if date.strftime('%b %d') in date_str:  # Match the day (e.g., "Jul 29")
                    planets = cols[1].text.strip().split()
                    aspect = cols[2].text.strip().split('(')[0]  # e.g., "Ven Jup" -> "Conjunction"
                    time_utc = "12:00"  # Default to 12:00 UT/GMT as per document
                    time_ist = utc_to_ist(time_utc)
                    transits.append({
                        "Planet": planets[0],  # First planet
                        "Time": time_ist,
                        "Position": f"{random.randint(0, 29)}°{random.randint(0, 59)}'{random.randint(0, 59)}\"",  # Placeholder
                        "Motion": random.choice(["D", "R"]),
                        "Nakshatra": random.choice(["Rohini", "Hasta", "Krittika", "Punarvasu"])
                    })
                    if len(planets) > 1:  # Add second planet if aspect involves two
                        transits.append({
                            "Planet": planets[1],
                            "Time": time_ist,
                            "Position": f"{random.randint(0, 29)}°{random.randint(0, 59)}'{random.randint(0, 59)}\"",
                            "Motion": random.choice(["D", "R"]),
                            "Nakshatra": random.choice(["Rohini", "Hasta", "Krittika", "Punarvasu"])
                        })
        logger.info(f"Fetched {len(transits)} transits from Astro-Seek")
        return transits if transits else None
    except Exception as e:
        logger.error(f"Astro-Seek error: {str(e)}")
        st.warning(f"Could not fetch from Astro-Seek: {str(e)}")
        return None

def fetch_drik_panchang_data(date):
    """Attempt to scrape transit data from Drik Panchang"""
    try:
        url = f"https://www.drikpanchang.com/panchang/day-panchang.html?date={date.strftime('%d/%m/%Y')}"
        headers = {"User-Agent": get_random_user_agent()}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        transits = []
        for row in soup.select('table[class*="dpPanchangTable"] tr')[1:]:
            cols = row.select('td')
            if len(cols) >= 4:
                position = cols[1].text.strip()
                if not re.match(r"\d+°\d+'?\d*\"?", position):
                    position = f"{random.randint(0, 29)}°{random.randint(0, 59)}'{random.randint(0, 59)}\""
                time_str = cols[0].text.strip() if len(cols) > 0 and re.match(r"\d{2}:\d{2}", cols[0].text.strip()) else None
                time = time_str if time_str else str(datetime.strptime(f"{date.strftime('%Y-%m-%d')} {random.randint(0, 23):02d}:{random.randint(0, 59):02d}", "%Y-%m-%d %H:%M")).split()[1][:5]
                transits.append({
                    "Planet": cols[0].text.strip().split()[0] if len(cols) > 0 else random.choice(list(VEDIC_PLANETS.keys())),
                    "Time": time,
                    "Position": position,
                    "Motion": "R" if "Retrograde" in cols[2].text else "D",
                    "Nakshatra": cols[3].text.strip() if len(cols) > 3 else random.choice(["Rohini", "Hasta", "Krittika", "Punarvasu"])
                })
        logger.info(f"Fetched {len(transits)} transits from Drik Panchang")
        return transits if transits else None
    except Exception as e:
        logger.error(f"Drik Panchang error: {str(e)}")
        st.warning(f"Could not fetch from Drik Panchang: {str(e)}")
        return None

def fetch_astronomics_data(date):
    """Fetch data from Astro-Seek with fallback to Drik Panchang and sample data"""
    # Try Astro-Seek
    transits = fetch_astro_seek_data(date)
    if transits:
        return transits
    
    # Try Drik Panchang
    transits = fetch_drik_panchang_data(date)
    if transits:
        return transits
    
    # Fallback to sample data
    logger.info("Using sample data as fallback")
    st.info("Using sample data (real data unavailable)")
    return generate_sample_data(date)

def generate_sample_data(date):
    """Generate sample data with varied times and Nakshatras for the day"""
    planets = list(VEDIC_PLANETS.keys())
    nakshatras = ["Rohini", "Hasta", "Krittika", "Punarvasu", "Mrigashira", "Dhanishta"]
    return [{
        "Planet": planet,
        "Time": str(datetime.strptime(f"{date.strftime('%Y-%m-%d')} {random.randint(0, 23):02d}:{random.randint(0, 59):02d}", "%Y-%m-%d %H:%M")).split()[1][:5],
        "Position": f"{random.randint(0, 29)}°{random.randint(0, 59)}'{random.randint(0, 59)}\"",
        "Motion": random.choice(["D", "R"]),
        "Nakshatra": random.choice(nakshatras)
    } for planet in planets]  # One transit per planet with random time

def calculate_aspect(position):
    """Calculate aspect based on zodiac position with robust parsing"""
    try:
        match = re.match(r"(\d+)°(\d+)'?(\d*)\"?", position)
        if not match:
            logger.warning(f"Invalid position format: {position}")
            return random.choice(["Conjunction", "Sextile", "Square", "Trine"])
        deg = float(match.group(1))
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
    except Exception as e:
        logger.error(f"Error in calculate_aspect: {str(e)}")
    return random.choice(["Conjunction", "Sextile", "Square", "Trine"])

def determine_effect(planet, aspect, rulers, motion, symbol, nakshatra):
    """Determine market effect with motion and Nakshatra consideration"""
    strength = 1.3 if motion == "R" else 1.0
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
    """Generate trading signals from all transit data (no symbol filtering)"""
    config = SYMBOL_CONFIG.get(symbol, {})  # Used only for effect calculation
    signals = []
    
    for transit in transits:
        planet = transit.get("Planet")
        if not planet:
            continue  # Skip invalid entries
            
        aspect = calculate_aspect(transit.get("Position", "0°0'0\""))
        effect, impact = determine_effect(planet, aspect, config.get("rulers", {}), transit.get("Motion", "D"), symbol, transit.get("Nakshatra", "Unknown"))
        
        signals.append({
            "Time": transit.get("Time", "00:00"),
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, planet)})",
            "Aspect": aspect,
            "Nakshatra": transit.get("Nakshatra", "Unknown"),
            "Impact": impact,
            "Effect": effect,
            "Action": get_trading_action(effect),
            "Interpretation": generate_interpretation(planet, aspect, symbol, transit.get("Nakshatra", "Unknown"))
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
            try:
                # Fetch transit data
                transits = fetch_astronomics_data(selected_date)
                
                if not transits:
                    st.warning("No transit data available")
                    st.stop()
                
                signals = generate_signals(symbol, transits)
                
                if not signals:
                    st.warning("No planetary aspects found for the selected date")
                    st.stop()
                
                # Create and display DataFrame
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
                    hide_index=True
                )
            except Exception as e:
                logger.error(f"Error in main: {str(e)}")
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
