import streamlit as st
from datetime import datetime
import pandas as pd
import pytz
import math
from astropy.coordinates import get_body, GeocentricTrueEcliptic
from astropy.time import Time

# === Streamlit Page Config ===
st.set_page_config(page_title="🌓 Astro Gann Grid", layout="wide", page_icon="📈")
st.title("📈 Astro Gann Tool with Moon Nakshatra, D9 & Gann Square of 9")

# === Sidebar Inputs ===
with st.sidebar:
    st.header("🛠️ Input Controls")

    symbol = st.text_input("Symbol", value="NIFTY")
    price_input = st.number_input("CMP (Current Market Price)", min_value=1.0, value=25000.0)
    date_input = st.date_input("Date", value=datetime.today())
    time_input = st.time_input("Time", value=datetime.now().time())
    angle_step = st.selectbox("📐 Gann Angle Step", [30, 45, 60, 90], index=1)
    steps = st.slider("Steps", 5, 50, 10)

# === Astro Time Setup ===
dt = datetime.combine(date_input, time_input)
tz = pytz.timezone("Asia/Kolkata")
dt = tz.localize(dt)
astro_time = Time(dt)

# === Astro Calculations ===
moon = get_body('moon', astro_time)
moon_coords = moon.transform_to(GeocentricTrueEcliptic(equinox=astro_time))
moon_longitude = moon_coords.lon.deg
moon_degree = round(moon_longitude, 2)

# === Zodiac & Nakshatra ===
zodiac_signs = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]
zodiac_name = zodiac_signs[int(moon_longitude // 30)]

nakshatras = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]
nakshatra_name = nakshatras[int((moon_longitude * 3) // 40)]
d9_sign_index = int((moon_longitude % 40) // (40 / 12))
d9_sign_name = zodiac_signs[d9_sign_index % 12]

# === Sentiment Logic ===
bullish_nakshatras = {"Ashwini", "Bharani", "Rohini", "Pushya", "Hasta", "Swati", "Anuradha", "Shravana", "Revati"}
bearish_nakshatras = {"Ardra", "Magha", "Purva Phalguni", "Chitra", "Vishakha", "Jyeshtha", "Mula", "Shatabhisha"}

astro_score = 1 if nakshatra_name in bullish_nakshatras else -1 if nakshatra_name in bearish_nakshatras else 0
sentiment = "🟢 Bullish" if astro_score > 0 else "🔴 Bearish" if astro_score < 0 else "⚪ Neutral"

# === Display Astro Info ===
col1, col2, col3 = st.columns(3)
col1.metric("🌕 Moon Degree", f"{moon_degree}°", zodiac_name)
col2.metric("🌌 Nakshatra", nakshatra_name, sentiment)
col3.metric("🔯 D9 Sign", d9_sign_name)

st.markdown("---")

# === Gann Square of 9 Aligned Grid ===
with st.expander("📊 Gann Square of 9 Levels (Based on Angle Steps)", expanded=True):
    base_sqrt = math.sqrt(price_input)

    def get_price_from_angle(base_sqrt, angle_deg):
        new_sqrt = base_sqrt + (angle_deg / 360)
        return round(new_sqrt ** 2, 2)

    def get_zodiac_from_deg(deg):
        return zodiac_signs[int((deg % 360) // 30)]

    angles = [(i * angle_step) % 360 for i in range(1, steps + 1)]

    buy_levels, sell_levels = [], []

    for i, angle in enumerate(angles, 1):
        buy_deg = angle % 360
        buy_price = get_price_from_angle(base_sqrt, buy_deg)
        buy_zodiac = get_zodiac_from_deg(buy_deg)

        sell_deg = (360 - angle) % 360
        sell_price = get_price_from_angle(base_sqrt, -angle)
        sell_zodiac = get_zodiac_from_deg(sell_deg)

        buy_levels.append({
            "Step": i,
            "🟢 Buy Level": f"**{buy_price}**",
            "Buy Deg": round(buy_deg, 2),
            "Buy Zodiac": buy_zodiac
        })

        sell_levels.append({
            "🔴 Sell Level": f"**{sell_price}**",
            "Sell Deg": round(sell_deg, 2),
            "Sell Zodiac": sell_zodiac
        })

    gann_square_df = pd.DataFrame({
        "Step": [x["Step"] for x in buy_levels],
        "🟢 Buy Level": [x["🟢 Buy Level"] for x in buy_levels],
        "Buy Deg": [x["Buy Deg"] for x in buy_levels],
        "Buy Zodiac": [x["Buy Zodiac"] for x in buy_levels],
        "🔴 Sell Level": [x["🔴 Sell Level"] for x in sell_levels],
        "Sell Deg": [x["Sell Deg"] for x in sell_levels],
        "Sell Zodiac": [x["Sell Zodiac"] for x in sell_levels]
    })

    st.dataframe(gann_square_df, use_container_width=True, hide_index=True)

# === Notes Section ===
with st.expander("📘 Notes"):
    st.markdown("""
    - **Gann Square of 9** calculates levels from the square root of CMP.
    - Buy levels follow positive angle steps; Sell levels mirror in reverse.
    - Each degree is mapped to a zodiac sign (30° per sign).
    - Works well when combined with astro signals and Nakshatra-based filters.
    """) 
