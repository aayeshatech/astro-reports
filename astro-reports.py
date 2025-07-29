import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import random

# === Vedic Names ===
VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu"
}

# === Symbol Rulership Aspects ===
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

# === Aspect Determination Based on Zodiac Degree ===
def get_aspect_for_position(zodiac_pos):
    try:
        degree = float(zodiac_pos.split('°')[0])
    except:
        degree = random.uniform(0, 360)

    if degree % 180 == 0:
        return "Opposition"
    elif degree % 120 == 0:
        return "Trine"
    elif degree % 90 == 0:
        return "Square"
    elif degree % 60 == 0:
        return "Sextile"
    elif degree % 30 == 0:
        return "Conjunction"
    else:
        return random.choice(["Sextile", "Square", "Trine"])

# === Interpretation Generator ===
def generate_interpretation(planet, aspect, symbol):
    action_words = {
        "Conjunction": "influencing",
        "Sextile": "supporting",
        "Square": "pressuring",
        "Trine": "benefiting",
        "Opposition": "challenging"
    }
    return f"{VEDIC_PLANETS.get(planet, planet)}'s {aspect.lower()} is {action_words.get(aspect, 'affecting')} {symbol.lower()} market."

# === Impact Evaluator ===
def determine_effect(planet, aspect, planetary_effects):
    if planet in planetary_effects:
        if aspect in planetary_effects[planet]["strong"]:
            return "Strong Bullish", f"+{random.uniform(0.8, 2.0):.1f}%"
        elif aspect in planetary_effects[planet]["weak"]:
            return "Strong Bearish", f"-{random.uniform(0.8, 2.0):.1f}%"
    return random.choice(["Mild Bullish", "Mild Bearish", "Neutral"]), f"{random.uniform(-0.5, 0.5):.1f}%"

def get_action(effect):
    if "Strong Bullish" in effect:
        return "GO LONG"
    elif "Mild Bullish" in effect:
        return "Consider LONG"
    elif "Strong Bearish" in effect:
        return "GO SHORT"
    elif "Mild Bearish" in effect:
        return "Consider SHORT"
    return "HOLD"

# === HTML Parser for Astronomics ===
def fetch_astronomics_data(date):
    url = f"https://data.astronomics.ai/almanac/?date={date.strftime('%Y-%m-%d')}"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if not table:
            return []

        rows = table.find_all("tr")[1:]  # Skip header
        data = []
        for row in rows:
            cols = [td.text.strip() for td in row.find_all("td")]
            if len(cols) >= 12:
                data.append({
                    "Planet": cols[0],
                    "Time": cols[2],
                    "Motion": cols[3],
                    "Sign Lord": cols[4],
                    "Star Lord": cols[5],
                    "Sub Lord": cols[6],
                    "Zodiac": cols[7],
                    "Nakshatra": cols[8],
                    "Pada": cols[9],
                    "Pos in Zodiac": cols[10],
                    "Declination": cols[11],
                })
        return data
    except Exception as e:
        return []

# === Signal Generator ===
def generate_transits(symbol, selected_date):
    data = fetch_astronomics_data(selected_date)
    effects = SYMBOL_RULERSHIPS.get(symbol, {})
    timeline = []

    for item in data:
        planet = item["Planet"]
        aspect = get_aspect_for_position(item["Pos in Zodiac"])
        effect, impact = determine_effect(planet, aspect, effects)
        action = get_action(effect)
        interpretation = generate_interpretation(planet, aspect, symbol)

        timeline.append({
            "Time": item["Time"][:5],
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, planet)})",
            "Aspect": aspect,
            "Effect": effect,
            "Impact": impact,
            "Action": action,
            "Interpretation": interpretation
        })

    return pd.DataFrame(timeline)

# === Streamlit App ===
def main():
    st.set_page_config(page_title="🔯 Vedic Astro Signals", layout="wide")
    st.title("📊 Vedic Astro Aspect Signal Timeline")

    symbol = st.selectbox("Select Symbol", list(SYMBOL_RULERSHIPS.keys()), index=0)
    selected_date = st.date_input("Select Date", datetime.today())

    if st.button("🔮 Generate Astro Report"):
        with st.spinner("Fetching astro signals..."):
            df = generate_transits(symbol, selected_date)

        if df.empty:
            st.warning("No planetary data found for selected date.")
        else:
            def style_effect(val):
                return f"background-color: {'#27ae60' if 'Bullish' in val else '#c0392b' if 'Bearish' in val else '#95a5a6'}; color: white;"

            def style_action(val):
                return f"background-color: {'#2ecc71' if 'LONG' in val else '#e74c3c' if 'SHORT' in val else '#95a5a6'}; color: white; font-weight: bold"

            styled_df = df.style\
                .applymap(style_effect, subset=['Effect'])\
                .applymap(style_action, subset=['Action'])

            st.dataframe(styled_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
