import streamlit as st
import swisseph as swe
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Nakshatra data
nakshatras = [
    ("Ashwini", 0, 13+20/60), ("Bharani", 13+20/60, 26+40/60), ("Krittika", 26+40/60, 40),
    ("Rohini", 40, 53+20/60), ("Mrigashira", 53+20/60, 66+40/60), ("Ardra", 66+40/60, 80),
    ("Punarvasu", 80, 93+20/60), ("Pushya", 93+20/60, 106+40/60), ("Ashlesha", 106+40/60, 120),
    ("Magha", 120, 133+20/60), ("Purva Phalguni", 133+20/60, 146+40/60), ("Uttara Phalguni", 146+40/60, 160),
    ("Hasta", 160, 173+20/60), ("Chitra", 173+20/60, 186+40/60), ("Swati", 186+40/60, 200),
    ("Vishakha", 200, 213+20/60), ("Anuradha", 213+20/60, 226+40/60), ("Jyeshtha", 226+40/60, 240),
    ("Mula", 240, 253+20/60), ("Purva Ashadha", 253+20/60, 266+40/60), ("Uttara Ashadha", 266+40/60, 280),
    ("Shravana", 280, 293+20/60), ("Dhanishta", 293+20/60, 306+40/60), ("Shatabhisha", 306+40/60, 320),
    ("Purva Bhadrapada", 320, 333+20/60), ("Uttara Bhadrapada", 333+20/60, 346+40/60), ("Revati", 346+40/60, 360)
]

# Zodiac signs and houses
zodiac_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
houses = [f"House {i}" for i in range(1, 13)]

# Function to calculate Nakshatra and Pada
def get_nakshatra_pada(degree):
    for nak, start, end in nakshatras:
        if start <= degree < end:
            pada = int((degree - start) // (13+20/60 / 4)) + 1
            return nak, pada
    return "Unknown", 0

# Function to get zodiac sign and house
def get_zodiac_house(degree):
    sign_index = int(degree // 30) % 12
    house_index = int(degree // 30) % 12
    return zodiac_signs[sign_index], houses[house_index]

# Function to calculate planetary positions
def get_planetary_positions(date_time):
    utc_offset = 5.5  # IST is UTC+5:30
    utc_datetime = date_time - timedelta(hours=utc_offset)
    jd = swe.julday(utc_datetime.year, utc_datetime.month, utc_datetime.day, 
                   utc_datetime.hour + utc_datetime.minute/60.0 + utc_datetime.second/3600.0)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    
    planets = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE, "Ketu": swe.MEAN_NODE
    }
    
    positions = []
    for planet, pid in planets.items():
        lon_trop = swe.calc_ut(jd, pid)[0][0]
        lon_sid = (lon_trop - ayanamsa) % 360
        if planet == "Ketu":
            lon_sid = (lon_sid + 180) % 360
        sign, house = get_zodiac_house(lon_sid)
        nak, pada = get_nakshatra_pada(lon_sid % 30 + (int(lon_sid // 30) * 30))
        is_retro = "N/A"
        if planet not in ["Rahu", "Ketu"]:
            result = swe.calc_ut(jd, pid)
            if len(result[0]) > 3:
                is_retro = "Yes" if result[0][3] < 0 else "No"
        positions.append({
            "Planet": planet,
            "Sign": sign,
            "Degree": f"{int(lon_sid % 30)}° {int((lon_sid % 1) * 60)}'",
            "House": house,
            "Nakshatra": nak,
            "Pada": pada,
            "Retrograde": is_retro,
            "Date": date_time.strftime("%Y-%m-%d %H:%M IST")
        })
    return pd.DataFrame(positions)

# Function to calculate aspects
def get_aspects(positions):
    aspects = []
    planets = positions["Planet"].tolist()
    degrees = positions["Degree"].apply(lambda x: float(x.split('°')[0]) + float(x.split('°')[1].split("'")[0])/60)
    for i, p1 in enumerate(planets[:-1]):
        for j, p2 in enumerate(planets[i+1:], start=i+1):
            deg1 = degrees[i]
            deg2 = degrees[j]
            diff = min((deg2 - deg1) % 360, (deg1 - deg2) % 360)
            if diff < 1:  # Conjunction
                aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Conjunction", "Degree": f"{diff:.2f}°"})
            elif 59 < diff < 61:  # Sextile
                aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Sextile", "Degree": f"{diff:.2f}°"})
            elif 89 < diff < 91:  # Square
                aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Square", "Degree": f"{diff:.2f}°"})
            elif 119 < diff < 121:  # Trine
                aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Trine", "Degree": f"{diff:.2f}°"})
    return pd.DataFrame(aspects)

# Function to determine strong buy/sell signals based on aspects
def get_trading_signal(aspects):
    is_bullish = any(aspect["Aspect"] in ["Trine", "Sextile"] for _, aspect in aspects.iterrows())
    is_bearish = any(aspect["Aspect"] in ["Square", "Conjunction"] for _, aspect in aspects.iterrows())
    if is_bullish and not is_bearish:
        return "Strong Buy", "green"
    elif is_bearish and not is_bullish:
        return "Strong Sell", "red"
    else:
        return "Hold", "black"

# Streamlit app
st.title("Astro Market Analyzer")

# Tabs
tab1, tab2 = st.tabs(["Planetary Report", "Stock Search"])

# Planetary Report Tab
with tab1:
    st.header("Planetary Transits Report")
    year = datetime.now().year
    
    st.subheader(f"July {year} Transits")
    july_transits = []
    for day in range(1, 32):  # Iterate through July days
        try:
            date = datetime(year, 7, day, 9, 0)  # 9:00 AM IST
            positions = get_planetary_positions(date)
            july_transits.append(positions)
        except ValueError:
            break  # Stop at end of month
    july_df = pd.concat(july_transits, ignore_index=True)
    st.dataframe(july_df[["Planet", "Sign", "Degree", "House", "Nakshatra", "Pada", "Retrograde", "Date"]])
    july_aspects = pd.concat([get_aspects(df) for df in july_transits], ignore_index=True)
    if not july_aspects.empty:
        st.subheader("July Aspects")
        st.dataframe(july_aspects)

    st.subheader(f"August {year} Transits")
    aug_transits = []
    for day in range(1, 32):  # Iterate through August days
        try:
            date = datetime(year, 8, day, 9, 0)  # 9:00 AM IST
            positions = get_planetary_positions(date)
            aug_transits.append(positions)
        except ValueError:
            break  # Stop at end of month
    aug_df = pd.concat(aug_transits, ignore_index=True)
    st.dataframe(aug_df[["Planet", "Sign", "Degree", "House", "Nakshatra", "Pada", "Retrograde", "Date"]])
    aug_aspects = pd.concat([get_aspects(df) for df in aug_transits], ignore_index=True)
    if not aug_aspects.empty:
        st.subheader("August Aspects")
        st.dataframe(aug_aspects)

# Stock Search Tab
with tab2:
    st.header("Stock Search")
    symbol = st.text_input("Enter Stock Symbol", "NIFTY")
    start_date = st.date_input("Start Date", datetime(2025, 7, 29))
    start_time = st.time_input("Start Time (IST)", datetime(2025, 7, 29, 9, 0).time())
    end_date = st.date_input("End Date", datetime(2025, 7, 29))
    end_time = st.time_input("End Time (IST)", datetime(2025, 7, 29, 15, 0).time())
    if st.button("Search"):
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        if start_datetime > end_datetime:
            st.error("End datetime must be after start datetime.")
        else:
            timeline = []
            current_time = start_datetime
            while current_time <= end_datetime:
                positions = get_planetary_positions(current_time)
                aspects = get_aspects(positions)
                signal, color = get_trading_signal(aspects)
                timeline.append({
                    "DateTime": current_time.strftime("%Y-%m-%d %H:%M IST"),
                    "Planetary Transit": ", ".join([f"{row['Planet']} in {row['Sign']} {row['Degree']}" for _, row in positions.iterrows()]),
                    "Signal": signal,
                    "Color": color
                })
                current_time += timedelta(minutes=15)  # 15-minute intraday intervals
            timeline_df = pd.DataFrame(timeline)
            st.dataframe(timeline_df.style.apply(lambda x: ['color: {}'.format(x.Color) for _ in x], axis=1))

# Instructions
st.markdown("""
### Instructions
1. Install dependencies: `pip install -r requirements.txt` and `pip install pyswisseph`.
2. Run the app: `streamlit run script.py`.
3. Use the 'Planetary Report' tab to view monthly transits with dates.
4. Use the 'Stock Search' tab to input a stock symbol, date range with times, and analyze the intraday timeline.
5. Ensure Swiss Ephemeris data files are installed[](https://pyswisseph.readthedocs.io/en/latest/installation.html).
""")
