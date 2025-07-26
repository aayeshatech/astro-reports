# astro_timing_report.py

import streamlit as st
from datetime import datetime, timedelta, time as dtime
import pandas as pd
from astropy.coordinates import get_body, solar_system_ephemeris
from astropy.coordinates import get_body_barycentric_posvel
from astropy.time import Time
import astropy.units as u
import pytz
import math

# ========== Streamlit UI ==============
st.set_page_config(page_title="🔮 Astro Timing Bullish/Bearish Report", layout="wide")
st.title("🔮 Astro Market Signal Generator")

# Input date and market type
input_date = st.date_input("Select Market Date", datetime.now().date())
market_type = st.selectbox("Choose Market Type", ["Indian Market (9:15 AM - 3:30 PM)", "Global Market (6:00 AM - 12:00 AM)"])

# Setup market hours
if "Indian" in market_type:
    market_open = dtime(9, 15)
    market_close = dtime(15, 30)
else:
    market_open = dtime(6, 0)
    market_close = dtime(23, 59)

# Convert to datetime range with 10-min steps
tz = pytz.timezone('Asia/Kolkata')
date_start = tz.localize(datetime.combine(input_date, market_open))
date_end = tz.localize(datetime.combine(input_date, market_close))

# Define planetary pairs and aspect degrees
planets = ["moon", "mars", "mercury", "venus", "sun", "jupiter", "saturn"]
aspects = {
    "Conjunction": 0,
    "Opposition": 180,
    "Square": 90,
    "Trine": 120,
    "Sextile": 60
}

# Function to calculate angular separation between two planets
def get_angle(p1, p2, t):
    with solar_system_ephemeris.set('de432s'):
        pos1 = get_body(p1, t)
        pos2 = get_body(p2, t)
        lon1 = pos1.geocentrictrueecliptic.lon.deg
        lon2 = pos2.geocentrictrueecliptic.lon.deg
        angle = abs(lon1 - lon2) % 360
        if angle > 180:
            angle = 360 - angle
        return angle

# Collect aspect events
events = []
current_time = date_start
while current_time <= date_end:
    t = Time(current_time)
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            angle = get_angle(planets[i], planets[j], t)
            for asp_name, asp_deg in aspects.items():
                if abs(angle - asp_deg) <= 2:  # 2° orb
                    sentiment = "🟢 Bullish" if asp_name in ["Conjunction", "Trine", "Sextile"] else "🔴 Bearish"
                    events.append({
                        "Time": current_time.strftime("%H:%M"),
                        "Aspect": f"{planets[i].capitalize()} {asp_name} {planets[j].capitalize()}",
                        "Angle": round(angle, 1),
                        "Sentiment": sentiment
                    })
    current_time += timedelta(minutes=10)

# Show results
df = pd.DataFrame(events)
if not df.empty:
    st.success(f"Found {len(df)} Astro Signals on {input_date.strftime('%d-%b-%Y')}")
    st.dataframe(df, use_container_width=True)
    
    # Optional grouping
    bull = df[df['Sentiment'].str.contains("Bullish")]
    bear = df[df['Sentiment'].str.contains("Bearish")]
    
    st.subheader("🟢 Bullish Timing")
    st.dataframe(bull[['Time', 'Aspect']], use_container_width=True)

    st.subheader("🔴 Bearish Timing")
    st.dataframe(bear[['Time', 'Aspect']], use_container_width=True)
else:
    st.warning("No major aspects found in the market hours on this date.")
