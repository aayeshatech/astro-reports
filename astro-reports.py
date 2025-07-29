import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta

# Configs

VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu",
    "Uranus": "Uranus", "Neptune": "Neptune", "Pluto": "Pluto"
}

SYMBOL_CONFIG = {
    "GOLD": {
        "planets": ["Sun", "Venus", "Saturn"],
        "rulers": {
            "Sun": {"strong": ["Trine", "Sextile"], "weak": ["Square", "Opposition"]},
            "Venus": {"strong": ["Trine", "Conjunction"], "weak": ["Square"]},
            "Saturn": {"strong": ["Conjunction"], "weak": ["Opposition"]}
        }
    },
    "SILVER": {
        "planets": ["Moon", "Venus"],
        "rulers": {
            "Moon": {"strong": ["Trine", "Sextile"], "weak": ["Square"]}
        }
    },
    "CRUDE": {
        "planets": ["Jupiter", "Neptune"],
        "rulers": {
            "Jupiter": {"strong": ["Trine"], "weak": ["Square"]}
        }
    },
    "NIFTY": {
        "planets": ["Sun", "Mars"],
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

# Simple fallback Moon Nakshatra segments generator (replace with real scraped data source)
def fetch_moon_nakshatra_segments(selected_date):
    # Example fixed segments for demonstration
    d = datetime.combine(selected_date, time(0,0))
    segments = [
        {"start": d, "end": d+timedelta(hours=10), "nakshatra": "Uttara Phalguni"},
        {"start": d+timedelta(hours=10), "end": d+timedelta(hours=19, minutes=27), "nakshatra": "Hasta"},
        {"start": d+timedelta(hours=19, minutes=27), "end": d+timedelta(hours=23, minutes=59), "nakshatra": "Chitra"}
    ]
    return segments

def calculate_aspect_mock(planet, nakshatra, symbol):
    # Basic mock logic: cyclic aspects by hash mod 3
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
        return "Strong Bullish", f"+{1.1 * nakshatra_boost:.1f}%"
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

def generate_interpretation(planet, aspect, symbol, nakshatra):
    vedic = VEDIC_PLANETS.get(planet, planet)
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
    planet = config["planets"][0]
    signals = []
    for seg in moon_segments:
        # Skip segments outside user time range
        seg_start = max(seg["start"], start_dt)
        seg_end = min(seg["end"], end_dt)
        if seg_end < start_dt or seg_start > end_dt:
            continue
        aspect = calculate_aspect_mock(planet, seg["nakshatra"], symbol)
        effect, impact = determine_effect(planet, aspect, config["rulers"], symbol, seg["nakshatra"])
        if effect not in {"Strong Bullish", "Strong Bearish"}:
            continue
        signals.append({
            "Time Window": f"{seg_start.strftime('%H:%M')} — {seg_end.strftime('%H:%M')}",
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, '')})",
            "Aspect": aspect,
            "Nakshatra": seg["nakshatra"],
            "Effect": effect,
            "Impact": impact,
            "Action": get_trading_action(effect),
            "Interpretation": generate_interpretation(planet, aspect, symbol, seg["nakshatra"])
        })
    return signals

def main():
    st.title("🌌 Vedic Astro Trading Signals")
    st.markdown("### Select Symbol, Date and Intraday Time Range")

    col1, col2, col3 = st.columns(3)
    with col1:
        symbol = st.selectbox("Select Symbol", list(SYMBOL_CONFIG.keys()))
    with col2:
        selected_date = st.date_input("Select Date", value=datetime.today())
    with col3:
        start_time = st.time_input("Start Time", value=time(9, 0))
        end_time = st.time_input("End Time", value=time(17, 0))

    start_dt = datetime.combine(selected_date, start_time)
    end_dt = datetime.combine(selected_date, end_time)
    if end_dt <= start_dt:
        st.warning("End time must be later than start time.")
        return

    if st.button("Generate Intraday Signals"):
        # Fetch Moon Nakshatra segments - replace with your actual data fetcher
        moon_segments = fetch_moon_nakshatra_segments(selected_date)
        if not moon_segments:
            st.warning("No Moon Nakshatra transit data found for selected date.")
            return
        signals = generate_intraday_signals(symbol, moon_segments, start_dt, end_dt)
        if signals:
            df = pd.DataFrame(signals)
            def color_effect(val):
                return f"background-color: {'#27ae60' if val == 'Strong Bullish' else '#e74c3c'}; color: white"
            def color_action(val):
                return f"background-color: {'#16a085' if val.startswith('STRONG BUY') else '#c0392b'}; color: white; font-weight: bold"
            styled = df.style.applymap(color_effect, subset=['Effect']).applymap(color_action, subset=['Action']).set_properties(**{'text-align': 'left'})
            st.dataframe(styled, use_container_width=True, hide_index=True)

            tabs = st.tabs(["Daily", "Weekly", "Monthly"])
            with tabs[0]:
                st.write("**Daily Analysis Placeholder**")
            with tabs[1]:
                st.write("**Weekly Analysis Placeholder**")
            with tabs[2]:
                st.write("**Monthly Analysis Placeholder**")
        else:
            st.warning("No strong bullish/bearish planetary events found for selected symbol and time range.")

if __name__ == "__main__":
    main()
