import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

# PLANET/Nakshatra Configurations (same as yours)
VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu",
    "Uranus": "Uranus", "Neptune": "Neptune", "Pluto": "Pluto"
}
SYMBOL_CONFIG = {
    "GOLD": {
        "planets": ["Sun", "Venus", "Saturn"],
        "colors": {"bullish": "#FFD700", "bearish": "#B8860B"},
        "rulers": {
            "Sun": {"strong": ["Trine", "Sextile"], "weak": ["Square", "Opposition"]},
            "Venus": {"strong": ["Trine", "Conjunction"], "weak": ["Square"]},
            "Saturn": {"strong": ["Conjunction"], "weak": ["Opposition"]}
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
NAKSHATRA_BOOST = {
    "SILVER": {"Moon": ["Rohini", "Hasta", "Shravana"], "boost": 1.2},
    "GOLD": {"Sun": ["Krittika", "Uttara Phalguni"], "boost": 1.1},
    "CRUDE": {"Jupiter": ["Punarvasu", "Vishakha"], "boost": 1.1},
    "NIFTY": {"Mars": ["Mrigashira", "Dhanishta"], "boost": 1.1}
}

st.set_page_config(page_title="Vedic Astro Trader", layout="wide")
st.title("🌌 Vedic Astro Trading Signals")
st.markdown("### Intraday & Symbol Astro Analysis")

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_transits_for_date(target_date):
    url = "https://www.astroccult.net/transit_of_planets_planetary_events.html"
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.content, "html.parser")

    # --- Parse Table ---
    table = soup.find("table", {"class": "tbltransit"})
    if not table:
        return []

    events = []
    for row in table.find_all("tr"):
        cols = [td.text.strip() for td in row.find_all("td")]
        if len(cols) < 3 or not re.search(r'\d{2}/\d{2}/\d{4}', " ".join(cols)):
            continue
        # Ex: 'Moon Hasta 29/07/2025 19:27'
        m = re.search(r"([A-Za-z]+)\s+([A-Za-z]+)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})", cols[1])
        if not m:
            continue
        planet, nakshatra, d, t = m.groups()
        dt = datetime.strptime(f"{d} {t}", "%d/%m/%Y %H:%M")
        events.append({"planet": planet, "nakshatra": nakshatra, "dt": dt})

    # Extract only the Moon's Nakshatra periods that touch the target date
    moon_nakshatra = [e for e in events if e["planet"].lower() == "moon"]
    segments = []
    for i in range(len(moon_nakshatra)-1):
        start, end = moon_nakshatra[i], moon_nakshatra[i+1]
        # If target date falls between start and end
        seg_start_date = start["dt"].date()
        seg_end_date = end["dt"].date()
        # check if start or end covers target_date
        if seg_start_date <= target_date <= seg_end_date:
            # clip to selected day boundaries
            seg_start = start["dt"] if seg_start_date == target_date else datetime.combine(target_date, datetime.min.time())
            seg_end = end["dt"] if seg_end_date == target_date else datetime.combine(target_date, datetime.max.time())
            segments.append({
                "start": seg_start,
                "end": seg_end,
                "nakshatra": start["nakshatra"]
            })
    # If only one segment on selected day (could happen at midnight)
    if not segments and moon_nakshatra:
        for e in moon_nakshatra:
            if e["dt"].date() == target_date:
                segments.append({"start": e["dt"], "end": datetime.combine(target_date, datetime.max.time()), "nakshatra": e["nakshatra"]})
    return segments

def calculate_aspect_mock(planet, nakshatra, symbol):
    # Dummy aspect assignment for demo (replace with more rules as needed)
    # Alternate between Trine, Square, Conjunction each Nakshatra
    code = hash((planet, nakshatra, symbol)) % 3
    return ["Trine", "Square", "Conjunction"][code]

def determine_effect(planet, aspect, rulers, symbol, nakshatra):
    strength = 1.0
    nakshatra_boost = 1.0
    # Special boost
    if symbol in NAKSHATRA_BOOST and planet in NAKSHATRA_BOOST[symbol]:
        if nakshatra in NAKSHATRA_BOOST[symbol][planet]:
            nakshatra_boost = NAKSHATRA_BOOST[symbol]["boost"]
    # Main aspect logic (just as in your function)
    if planet in rulers:
        if aspect in rulers[planet].get("strong", []):
            return "Strong Bullish", f"+{1.2 * strength * nakshatra_boost:.1f}%"
        elif aspect in rulers[planet].get("weak", []):
            return "Strong Bearish", f"-{1.2 * strength / nakshatra_boost:.1f}%"
    # Fallbacks
    if aspect == "Conjunction":
        return "Strong Bullish", f"+{1.1*nakshatra_boost:.1f}%"
    elif aspect == "Square":
        return "Strong Bearish", f"-1.0%"
    else:
        return "Neutral", "0.0%"

def get_trading_action(effect):
    return {
        "Strong Bullish": "STRONG BUY",
        "Mild Bullish": "BUY",
        "Neutral": "HOLD",
        "Mild Bearish": "SELL",
        "Strong Bearish": "STRONG SELL"
    }.get(effect, "HOLD")

def generate_interpretation(planet, aspect, symbol, nakshatra, with_planet=None):
    vedic = VEDIC_PLANETS.get(planet, planet)
    if with_planet:
        base = f"{vedic}-{with_planet} conjunction impacting {symbol}"
    else:
        base = {
            "Conjunction": f"{vedic} directly influencing {symbol}",
            "Sextile": f"Favorable energy from {vedic} for {symbol}",
            "Square": f"Challenging aspect from {vedic} on {symbol}",
            "Trine": f"Harmonious support from {vedic} for {symbol}",
            "Opposition": f"Polarized influence from {vedic} on {symbol}"
        }.get(aspect, f"{vedic} affecting {symbol} market")
    return f"{base} (Nakshatra: {nakshatra})"

def generate_intraday_signals(symbol, moon_segments):
    config = SYMBOL_CONFIG[symbol]
    signals = []
    planet = config["planets"][0]  # Use primary planet for this example
    
    for seg in moon_segments:
        seg_start_str = seg["start"].strftime("%H:%M")
        seg_end_str = seg["end"].strftime("%H:%M")
        nakshatra = seg["nakshatra"]
        aspect = calculate_aspect_mock(planet, nakshatra, symbol)
        effect, impact = determine_effect(planet, aspect, config["rulers"], symbol, nakshatra)
        if effect not in {"Strong Bullish", "Strong Bearish"}: continue
        signals.append({
            "Segment": f"{seg_start_str} — {seg_end_str}",
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, '')})",
            "Aspect": aspect,
            "Nakshatra": nakshatra,
            "Effect": effect,
            "Impact": impact,
            "Action": get_trading_action(effect),
            "Interpretation": generate_interpretation(planet, aspect, symbol, nakshatra),
        })
    return signals

def main():
    st.info("Vedic Astro Intraday Segments are powered by Moon Nakshatra changes. Only Strong Bullish/Bearish segments shown.")
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.selectbox("Select Symbol", list(SYMBOL_CONFIG.keys()), index=0)
    with col2:
        selected_date = st.date_input("Select Date", value=datetime(2025, 7, 29)).date()

    if st.button("Generate Intraday Signals"):
        with st.spinner("Fetching planetary transit data from Astroccult..."):
            moon_segs = fetch_transits_for_date(selected_date)
            signals = generate_intraday_signals(symbol, moon_segs)
            if signals:
                df = pd.DataFrame(signals)
                def color_effect(val):
                    return f"background-color: {'#27ae60' if val=='Strong Bullish' else '#e74c3c'};color:white"
                def color_action(val):
                    return f"background-color: {'#16a085' if val.startswith('STRONG BUY') else '#c0392b'};color:white;font-weight:bold"
                st.dataframe(
                    df.style.applymap(color_effect, subset=['Effect']).applymap(color_action, subset=['Action']).set_properties(**{'text-align': 'left'}),
                    use_container_width=True, hide_index=True
                )
                st.success("Signals generated for selected day and symbol. Only strong effect periods shown.")
            else:
                st.warning("No strong bullish/bearish planetary events found for this date/symbol.")

if __name__ == "__main__":
    main()
