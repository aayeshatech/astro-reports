import streamlit as st
import swisseph as swe
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime

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

# Zodiac signs
zodiac_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Function to calculate Nakshatra and Pada
def get_nakshatra_pada(degree):
    for nak, start, end in nakshatras:
        if start <= degree < end:
            pada = int((degree - start) // (13+20/60 / 4)) + 1
            return nak, pada
    return "Unknown", 0

# Function to get zodiac sign
def get_zodiac_sign(degree):
    sign_index = int(degree // 30)
    return zodiac_signs[sign_index]

# Function to calculate planetary positions
@st.cache_data
def get_planetary_positions(date_time, location="New Delhi"):
    try:
        # Convert to UTC for Swiss Ephemeris (IST is UTC+5:30)
        utc_offset = 5.5  # Hours
        utc_datetime = date_time - datetime.timedelta(hours=utc_offset)
        jd = swe.julday(utc_datetime.year, utc_datetime.month, utc_datetime.day, utc_datetime.hour + utc_datetime.minute/60.0)
        
        # Set sidereal mode (Lahiri Ayanamsa)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # Planetary IDs
        planets = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
            "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
            "Rahu": swe.MEAN_NODE, "Ketu": swe.MEAN_NODE
        }
        
        positions = []
        for planet, pid in planets.items():
            lon = swe.calc_ut(jd, pid)[0][0]
            if planet == "Ketu":
                lon = (lon + 180) % 360  # Ketu is opposite Rahu
            sign = get_zodiac_sign(lon)
            nak, pada = get_nakshatra_pada(lon % 30 + (int(lon // 30) * 30))
            positions.append({
                "Planet": planet,
                "Sign": sign,
                "Degree": f"{int(lon % 30)}° {int((lon % 1) * 60)}'",
                "Nakshatra": nak,
                "Pada": pada,
                "Longitude": lon
            })
        
        return pd.DataFrame(positions)
    except Exception as e:
        st.error(f"Error calculating planetary positions: {str(e)}")
        return None

# Function to create a polar chart
def create_polar_chart(df):
    if df is None or df.empty:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[1] * len(df),
        theta=df["Longitude"],
        text=df["Planet"],
        mode="markers+text",
        marker=dict(size=10, color="#FF6347", line=dict(width=2, color="#FFFFFF")),
        textposition="middle right"
    ))
    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                tickvals=list(range(0, 360, 30)),
                ticktext=zodiac_signs,
                rotation=90,
                direction="clockwise",
                gridcolor="#D3D3D3"
            ),
            radialaxis=dict(visible=False),
            bgcolor="#2F2F2F"
        ),
        showlegend=False,
        title="Planetary Positions in Zodiac",
        paper_bgcolor="#1F1F1F",
        font=dict(color="#FFFFFF"),
        margin=dict(t=50, b=50, l=50, r=50)
    )
    return fig

# Streamlit app
st.title("Vedic Astrology Transit Calculator")

# Input form
with st.form("transit_form"):
    date = st.date_input("Select Date", value=datetime.date(2025, 7, 29))
    start_time = st.time_input("Start Time (IST)", value=datetime.time(21, 29))
    end_time = st.time_input("End Time (IST)", value=datetime.time(21, 40))  # Adjusted to 09:40 PM IST
    location = st.text_input("Location", value="New Delhi")
    submit = st.form_submit_button("Calculate Transits")

# Process form submission
if submit:
    try:
        # Combine date and time
        start_datetime = datetime.datetime.combine(date, start_time)
        end_datetime = datetime.datetime.combine(date, end_time)
        
        # Validate time period
        if end_datetime <= start_datetime:
            st.error("End time must be after start time.")
        else:
            # Calculate positions for start time
            st.subheader(f"Transits at {start_datetime} IST ({location})")
            df_start = get_planetary_positions(start_datetime, location)
            
            if df_start is not None and not df_start.empty:
                st.dataframe(df_start[["Planet", "Sign", "Degree", "Nakshatra", "Pada"]])
                
                # Plot polar chart
                st.subheader("Zodiac Visualization")
                fig = create_polar_chart(df_start)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # Calculate positions for end time
                st.subheader(f"Transits at {end_datetime} IST ({location})")
                df_end = get_planetary_positions(end_datetime, location)
                
                if df_end is not None and not df_end.empty:
                    st.dataframe(df_end[["Planet", "Sign", "Degree", "Nakshatra", "Pada"]])
                    
                    # Check for changes
                    st.subheader("Changes During the Period")
                    changes = df_start.merge(df_end, on="Planet", suffixes=("_start", "_end"))
                    condition = ((changes["Sign_start"] != changes["Sign_end"]) |
                                 (changes["Nakshatra_start"] != changes["Nakshatra_end"]) |
                                 (changes["Pada_start"] != changes["Pada_end"]))
                    changes = changes[condition]
                    
                    if not changes.empty:
                        st.dataframe(changes[["Planet", "Sign_start", "Sign_end", "Nakshatra_start", "Nakshatra_end", "Pada_start", "Pada_end"]])
                    else:
                        st.write("No significant changes in sign, Nakshatra, or Pada during the period.")
                else:
                    st.error("Failed to calculate end time transits.")
            else:
                st.error("Failed to calculate start time transits. Check if pyswisseph is installed correctly.")
    except Exception as e:
        st.error(f"Error processing inputs: {str(e)}")

# Instructions for running
st.markdown("""
### Instructions
1. Install dependencies: `pip install -r requirements.txt` and `pip install pyswisseph`.
2. Run the app: `streamlit run script.py`.
3. Enter the date, start time, end time, and location, then click 'Calculate Transits'.
4. If no results appear, check the terminal for error messages or ensure `pyswisseph` is installed with ephemeris data[](https://pyswisseph.readthedocs.io/en/latest/installation.html).
""")
