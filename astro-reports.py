import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
import re

# --- CONFIGS ---
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

@st.cache_data(show_spinner=False, ttl=1800)
def fetch_transits_for_date(target_date):
    try:
        url = "https://www.astroccult.net/transit_of_planets_planetary_events.html"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        table = soup.find("table", {"class": "tbltransit"})
        if not table:
            st.warning("Transit table not found on astroccult.net")
            return []
        events = []
        for row in table.find_all("tr"):
            cols = [td.text.strip() for td in row.find_all("td")]
            if len(cols) < 3 or not re.search(r'\d{2}/\d{2}/\d{4}', " ".join(cols)):
                continue
            m = re.search(r"([A-Za-z]+)\s+([A-Za-z]+)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})", cols[1])
            if not m:
                continue
            planet, nakshatra, d, t = m.groups()
            dt = datetime.strptime(f"{d} {t}", "%d/%m/%Y %H:%M")
            events.append({"planet": planet, "nakshatra": nakshatra, "dt": dt})

        # Extract Moon Nakshatra segments overlapping the target date
        moon_nakshatra = [e for e in events if e["planet"].lower() == "moon"]
        segments = []
        date_start = datetime.combine(target_date, time.min)
        date_end = datetime.combine(target_date, time.max)
        for i in range(len(moon_nakshatra) - 1):
            seg_start = moon_nakshatra[i]["dt"]
            seg_end = moon_nakshatra[i + 1]["dt"]
            # segment overlaps with date?
            if seg_end > date_start and seg_start < date_end:
                segments.append({
                    "start": max(seg_start, date_start),
                    "end": min(seg_end, date_end),
                    "nakshatra": moon_nakshatra[i]["nakshatra"]
                })
        # If none found (start of data), fallback to last nakshatra before date covering full date
        if not segments and moon_nakshatra:
            for e in reversed(moon_nakshatra):
                if e["dt"] < date_start:
                    segments.append({
                        "start": date_start,
                        "end": date_end,
                        "nakshatra": e["nakshatra"]
                    })
                    break
        return segments
    except Exception as e:
        st.error(f"Error fetching transit data: {e}")
        return []

def calculate_aspect_mock(planet, nakshatra, symbol):
    # Dummy logic: rotates aspects for demonstration
    code = abs(hash((planet, nakshatra, symbol))) % 3
    return ["Trine", "Square", "Conjunction"][code]

def determine_effect(planet, aspect, rulers, symbol, nakshatra):
    strength = 1.0
    nakshatra_boost = 1.0
    if symbol in NAKSHATRA_BOOST and planet in NAKSHATRA_BOOST[symbol]:
        if nakshatra in NAKSHATRA_BOOST[symbol][planet]:
            nakshatra_boost = NAKSHATRA_BOOST[symbol]["boost"]

    if planet in rulers:
        if aspect in rulers[planet].get("strong", []):
            return "Strong Bullish", f"+{1.2 * strength * nakshatra_boost:.1f}%"
        elif aspect in rulers[planet].get("weak", []):
            return "Strong Bearish", f"-{1.2 * strength / nakshatra_boost:.1f}%"
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

def generate_intraday_signals(symbol, moon_segments, start_dt, end_dt):
    config = SYMBOL_CONFIG[symbol]
    signals = []
    planet = config["planets"][0]  # Primary planet for demo
    
    for seg in moon_segments:
        # Skip segments totally outside user selected time range
        if seg["end"] < start_dt or seg["start"] > end_dt:
            continue
        seg_start = max(seg["start"], start_dt)
        seg_end = min(seg["end"], end_dt)
        seg_start_str = seg_start.strftime("%H:%M")
        seg_end_str = seg_end.strftime("%H:%M")
        nakshatra = seg["nakshatra"]
        aspect = calculate_aspect_mock(planet, nakshatra, symbol)
        effect, impact = determine_effect(planet, aspect, config["rulers"], symbol, nakshatra)
        # Show only strong bullish/bearish
        if effect not in {"Strong Bullish", "Strong Bearish"}:
            continue
        signals.append({
            "Time Window": f"{seg_start_str} — {seg_end_str}",
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
    st.info("Pick a date and intraday time range to analyze Vedic Astro trading signals. Only strong bullish/bearish periods shown.")

    col1, col2, col3 = st.columns(3)
    with col1:
        symbol = st.selectbox("Select Symbol", list(SYMBOL_CONFIG.keys()), index=0)
    with col2:
        selected_date = st.date_input("Select Date", value=datetime(2025, 7, 29))
    with col3:
        start_time = st.time_input("Select Start Time", value=time(9, 0))
        end_time = st.time_input("Select End Time", value=time(17, 0))

    # Validate end_time not before start_time
    if end_time <= start_time:
        st.warning("End time must be later than start time.")
        return
    
    start_dt = datetime.combine(selected_date, start_time)
    end_dt = datetime.combine(selected_date, end_time)

    if st.button("Generate Intraday Signals"):
        with st.spinner("Fetching planetary transit data from Astroccult..."):
            moon_segs = fetch_transits_for_date(selected_date)
            if not moon_segs:
                st.warning("No Moon Nakshatra transit data found for this date.")
                return
            signals = generate_intraday_signals(symbol, moon_segs, start_dt, end_dt)
            if signals:
                df = pd.DataFrame(signals)
                def color_effect(val):
                    return f"background-color: {'#27ae60' if val == 'Strong Bullish' else '#e74c3c'};color:white"
                def color_action(val):
                    return f"background-color: {'#16a085' if val.startswith('STRONG BUY') else '#c0392b'};color:white;font-weight:bold"
                st.dataframe(
                    df.style.applymap(color_effect, subset=['Effect']).applymap(color_action, subset=['Action']).set_properties(**{'text-align': 'left'}),
                    use_container_width=True, hide_index=True
                )
                # Tabs placeholders for future extended reports:
                tabs = st.tabs(["Daily", "Weekly", "Monthly"])
                with tabs[0]:
                    st.write("**Daily Highlights:** Customize this with your daily analysis here.")
                with tabs[1]:
                    st.write("**Weekly Highlights:** Customize this with your weekly analysis here.")
                with tabs[2]:
                    st.write("**Monthly Highlights:** Customize this with your monthly analysis here.")
                st.success("Signals generated for the selected date and time range.")
            else:
                st.warning("No strong bullish/bearish planetary events found for this symbol and time range.")

if __name__ == "__main__":
    main()
