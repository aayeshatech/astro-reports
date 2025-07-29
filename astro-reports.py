import streamlit as st
import pandas as pd
import swisseph as swe
import requests
from datetime import datetime, timedelta
import pytz

# ===== SETTING UP SWISSEPH PATH =====
swe.set_ephe_path('.')  # Assuming ephemeris files are in the same directory

# ======= CONFIG =======
st.set_page_config(page_title="🪐 Astro Daily Report", layout="centered")
st.title("🪐 Astro Panchang Report with Backup API")

# ======= USER INPUT =======
selected_date = st.date_input("Select Date", datetime.today())
tz = pytz.timezone('Asia/Kolkata')
current_time = tz.localize(datetime.combine(selected_date, datetime.min.time()))
jul_day = swe.julday(current_time.year, current_time.month, current_time.day, 5.5)  # 5.5 for IST offset

st.write(f"Julian Day: {jul_day}")

# ======= PLANET LIST =======
planets = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
    'Ketu': swe.TRUE_NODE
}


# ====== FUNCTION: Get Planet Data from Swiss Ephemeris ======
def get_planet_data(jd):
    data = []
    try:
        for name, planet_id in planets.items():
            lon, _, _ = swe.calc_ut(jd, planet_id)
            sign = int(lon // 30) + 1
            degree = lon % 30
            data.append({
                'Planet': name,
                'Longitude': round(lon, 2),
                'Sign': sign,
                'Degree in Sign': round(degree, 2)
            })
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Swiss Ephemeris error: {e}")
        return None


# ====== FUNCTION: Fallback to API ======
def get_fallback_data(date):
    url = f"https://data.astronomics.ai/almanac?date={date.strftime('%Y-%m-%d')}&tz=Asia%2FKolkata"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            planet_positions = json_data.get("planetPositions", [])
            fallback_df = pd.DataFrame([
                {
                    "Planet": p["planet"],
                    "Sign": p["rasi"],
                    "Degree in Sign": round(float(p["degree"]), 2)
                }
                for p in planet_positions
            ])
            return fallback_df
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API request failed: {e}")
        return None


# ===== MAIN LOGIC =====
st.subheader("📍 Planetary Positions")
planet_df = get_planet_data(jul_day)

if planet_df is not None:
    st.dataframe(planet_df)
else:
    st.warning("Falling back to Astronomics API...")
    fallback_df = get_fallback_data(current_time)
    if fallback_df is not None:
        st.dataframe(fallback_df)
    else:
        st.error("No planetary data available from either source.")


# ===== FOOTER =====
st.markdown("---")
st.markdown("Powered by [Swiss Ephemeris](https://www.astro.com/swisseph/) & [Astronomics AI](https://data.astronomics.ai)")
