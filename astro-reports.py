import streamlit as st
import swisseph as swe
import pandas as pd
import requests
from datetime import datetime

# --- Streamlit Page Setup ---
st.set_page_config(page_title="🪐 Astro Market Report", layout="centered", page_icon="📊")
st.title("📊 Daily Astro Market Report")

# --- Load Swiss Ephemeris ---
swe.set_ephe_path("/usr/share/ephe")  # Modify if your ephemeris path is different

# --- Date Input ---
selected_date = st.date_input("Select Date", datetime.now().date())
utc_time = datetime.combine(selected_date, datetime.min.time())

# --- Function: Get Planetary Data ---
def get_planet_data(jd):
    planets = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mercury': swe.MERCURY,
        'Venus': swe.VENUS,
        'Mars': swe.MARS,
        'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN
    }

    rows = []
    for name, id in planets.items():
        lon, lat, dist = swe.calc_ut(jd, id)[0]
        rows.append({
            "Planet": name,
            "Longitude (°)": round(lon, 2),
            "Nakshatra": get_nakshatra(lon)
        })

    return pd.DataFrame(rows)

# --- Nakshatra Calculation ---
def get_nakshatra(longitude):
    nakshatras = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu",
        "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
        "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
        "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
        "Uttara Bhadrapada", "Revati"
    ]
    segment = int(longitude // (360 / 27))
    return nakshatras[segment % 27]

# --- Julian Day Calculation ---
jd = swe.julday(selected_date.year, selected_date.month, selected_date.day, 0)

# --- Generate Report ---
st.subheader("🪐 Planetary Positions & Nakshatra")
planet_df = get_planet_data(jd)
st.dataframe(planet_df)

# --- Optional: External API fetch ---
st.subheader("🌐 Optional External Astro API")

api_url = st.text_input("Enter Astro API URL (optional)", "")
if api_url:
    try:
        response = requests.get(api_url)
        data = response.json()
        st.write("API Response:")
        st.json(data)
    except requests.exceptions.JSONDecodeError:
        st.error("❌ Failed to parse JSON. Check the API response format.")
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
