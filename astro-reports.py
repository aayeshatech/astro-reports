import streamlit as st
import swisseph as swe
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Config
st.set_page_config(page_title="🔭 Astro Report", layout="wide")
st.title("🔭 Generate Daily Astro Report")

# Location Defaults
LAT, LON = 23.0225, 72.5714  # Ahmedabad, India
TZ = pytz.timezone('Asia/Kolkata')

# Input
selected_date = st.date_input("Select Date", datetime.now().date())
generate_btn = st.button("🧙‍♂️ Generate Astro Report")

# Astro Functions
nakshatra_list = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu',
    'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta',
    'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 'Mula', 'Purva Ashadha',
    'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada',
    'Uttara Bhadrapada', 'Revati'
]

def get_moon_position(jd):
    moon_long = swe.calc_ut(jd, swe.MOON)[0]
    return moon_long

def get_nakshatra_name(moon_long):
    index = int((moon_long % 360) / (360 / 27))
    return nakshatra_list[index]

def fetch_astro_data(date):
    data = []
    for hour in range(0, 24):
        dt = TZ.localize(datetime.combine(date, datetime.min.time()) + timedelta(hours=hour))
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)
        moon_long = get_moon_position(jd)
        nakshatra = get_nakshatra_name(moon_long)
        data.append({
            'Time': dt.strftime('%H:%M'),
            'Moon Longitude': round(moon_long, 2),
            'Nakshatra': nakshatra
        })
    return pd.DataFrame(data)

# MAIN EXECUTION
if generate_btn:
    try:
        df = fetch_astro_data(selected_date)
        st.success("✅ Astro Report Generated using Swiss Ephemeris.")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Failed to generate data: {str(e)}")
