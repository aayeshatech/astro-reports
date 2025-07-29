import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import random

# Vedic Names
VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu"
}

# Symbol Rulerships
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

# Aspect Based on Degree
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
        return random.choice(["Trine", "Square", "Sextile"])

# Interpretation
def generate_interpretation(planet, aspect, symbol):
    action_words = {
        "Conjunction": "influencing",
        "Sextile": "supporting",
        "Square": "pressuring",
        "Trine": "benefiting",
        "Opposition": "challenging"
    }
    return f"{VEDIC_PLANETS.get(planet, planet)}'s {aspect.lower()} is {action_words.get(aspect, 'affecting')} {symbol.lower()} market."

# Effect Detection
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

# Fetch Astro Data (With Fallback)
def fetch_astronomics_data(date):
    url_primary = f"https://data.astronomics.ai/almanac/?date={date.strftime('%Y-%m-%d')}"
    try:
        response = requests.get(url_primary, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")[1:]
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
            if data:
                return data, "Primary"
    except:
        pass

    # === Fallback from DrikPanchang ===
    try:
        drik_url = f"https://www.drikpanchang.com/panchang/day-panchang.html?date={date.strftime('%Y-%m-%d')}&geoname-id=1264527"
        drik_res = requests.get(drik_url, timeout=10)
        soup = BeautifulSoup(drik_res.text, "html.parser")
        table = soup.find("table", {"id": "planetary-positions-table"})
        if not table:
            return [], "None"

        rows = table.find_all("tr")[1:]
        data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 5:
                planet = cols[0].text.strip()
                position = cols[1].text.strip()
                sign = cols[2].text.strip()
                nakshatra = cols[3].text.strip()
                motion = cols[4].text.strip()
                data.append({
                    "Planet": planet,
                    "Time": "06:00",  # default time
                    "Motion": motion,
                    "Sign Lord": sign,
                    "Star Lord": nakshatra,
                    "Sub Lord": "",
                    "Zodiac": sign,
                    "Nakshatra": nakshatra,
                    "Pada": "1",
                    "Pos in Zodiac": position,
                    "Declination": "0"
                })
        return data, "Fallback"
    except:
        return [], "None"

# Generate Transit Table
def generate_transits(symbol, selected_date):
    data, source = fetch_astronomics_data(selected_date)
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

    return pd.DataFrame(timeline), source

# Streamlit UI
def main():
    st.set_page_config(page_title="🔯 Vedic Astro Signals", layout="wide")
    st.title("📊 Vedic Astro Aspect Signal Timeline")

    symbol = st.selectbox("Select Symbol", list(SYMBOL_RULERSHIPS.keys()), index=0)
    selected_date = st.date_input("Select Date", datetime.today())

    if st.button("🔮 Generate Astro Report"):
        with st.spinner("Fetching astro signals..."):
            df, source = generate_transits(symbol, selected_date)

        if df.empty:
            st.error("No data found from both astronomics.ai and drikpanchang.com.")
        else:
            if source == "Fallback":
                st.info("Fallback used: Data from DrikPanchang.com")
            elif source == "Primary":
                st.success("Data fetched from Astronomics.ai")

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
