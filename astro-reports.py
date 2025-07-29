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

# Planet weights for aspect strength
planet_weights = {
    "Sun": 1.5, "Moon": 1.3, "Mars": 1.2, "Mercury": 1.0,
    "Jupiter": 1.4, "Venus": 1.1, "Saturn": 1.3,
    "Rahu": 1.2, "Ketu": 1.2
}

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
        nak, pada = get_nakshatra_pada(lon_sid)
        is_retro = "N/A"
        if planet not in ["Rahu", "Ketu"]:
            result = swe.calc_ut(jd, pid)
            if len(result[0]) > 3:
                is_retro = "Yes" if result[0][3] < 0 else "No"
        
        # Fixed degree calculation
        degree_in_sign = lon_sid % 30
        degree_int = int(degree_in_sign)
        minute_int = int((degree_in_sign - degree_int) * 60)
        
        positions.append({
            "Planet": planet,
            "Sign": sign,
            "Degree": f"{degree_int}° {minute_int}'",
            "House": house,
            "Nakshatra": nak,
            "Pada": pada,
            "Retrograde": is_retro,
            "Date": date_time.strftime("%Y-%m-%d %H:%M IST")
        })
    return pd.DataFrame(positions)

# Function to calculate aspects with improved tolerance
def get_aspects(positions):
    aspects = []
    planets = positions["Planet"].tolist()
    degrees = positions["Degree"].apply(lambda x: float(x.split('°')[0]) + float(x.split('°')[1].split("'")[0])/60)
    
    # Add the full longitude to each degree (sign * 30 + degree)
    full_degrees = []
    for i, planet in enumerate(planets):
        sign_index = zodiac_signs.index(positions.iloc[i]["Sign"])
        full_degree = sign_index * 30 + degrees[i]
        full_degrees.append(full_degree)
    
    for i, p1 in enumerate(planets[:-1]):
        for j, p2 in enumerate(planets[i+1:], start=i+1):
            deg1 = full_degrees[i]
            deg2 = full_degrees[j]
            diff = min((deg2 - deg1) % 360, (deg1 - deg2) % 360)
            
            # Increased tolerance and added more aspects
            weight = (planet_weights.get(p1, 1.0) + planet_weights.get(p2, 1.0)) / 2
            
            if diff < 3:  # Conjunction with 3° tolerance
                aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Conjunction", 
                               "Degree": f"{diff:.2f}°", "Weight": weight})
            elif 57 < diff < 63:  # Sextile with 3° tolerance
                aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Sextile", 
                               "Degree": f"{diff:.2f}°", "Weight": weight})
            elif 87 < diff < 93:  # Square with 3° tolerance
                aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Square", 
                               "Degree": f"{diff:.2f}°", "Weight": weight})
            elif 117 < diff < 123:  # Trine with 3° tolerance
                aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Trine", 
                               "Degree": f"{diff:.2f}°", "Weight": weight})
            elif 177 < diff < 183:  # Opposition with 3° tolerance
                aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Opposition", 
                               "Degree": f"{diff:.2f}°", "Weight": weight})
    return pd.DataFrame(aspects)

# Improved function to determine trading signals
def get_trading_signal(aspects):
    if aspects.empty:
        return "Neutral", "gray", 0, 0
    
    bullish_score = 0
    bearish_score = 0
    
    for _, aspect in aspects.iterrows():
        weight = aspect["Weight"]
        if aspect["Aspect"] in ["Trine", "Sextile"]:
            bullish_score += weight
        elif aspect["Aspect"] in ["Square", "Opposition"]:
            bearish_score += weight
        elif aspect["Aspect"] == "Conjunction":
            # Conjunction can be bullish or bearish depending on planets
            if aspect["Planet1"] in ["Jupiter", "Venus"] or aspect["Planet2"] in ["Jupiter", "Venus"]:
                bullish_score += weight * 0.8
            elif aspect["Planet1"] in ["Mars", "Saturn", "Rahu", "Ketu"] or aspect["Planet2"] in ["Mars", "Saturn", "Rahu", "Ketu"]:
                bearish_score += weight * 0.8
    
    # Determine signal based on scores
    if bullish_score > bearish_score * 1.5:
        return "Strong Buy", "green", bullish_score, bearish_score
    elif bearish_score > bullish_score * 1.5:
        return "Strong Sell", "red", bullish_score, bearish_score
    elif bullish_score > bearish_score:
        return "Buy", "lightgreen", bullish_score, bearish_score
    elif bearish_score > bullish_score:
        return "Sell", "lightcoral", bullish_score, bearish_score
    else:
        return "Neutral", "gray", bullish_score, bearish_score

# Function to get significant transits (changes in planetary positions)
def get_significant_transits(current_positions, previous_positions=None):
    if previous_positions is None:
        # For the first timestamp, show all positions
        return [f"{row['Planet']} in {row['Sign']} {row['Degree']}" for _, row in current_positions.iterrows()]
    
    significant_changes = []
    
    # Compare current and previous positions
    for _, current_row in current_positions.iterrows():
        planet = current_row["Planet"]
        previous_row = previous_positions[previous_positions["Planet"] == planet]
        
        if not previous_row.empty:
            prev_sign = previous_row.iloc[0]["Sign"]
            prev_degree = previous_row.iloc[0]["Degree"]
            prev_nakshatra = previous_row.iloc[0]["Nakshatra"]
            
            # Check for sign change
            if current_row["Sign"] != prev_sign:
                significant_changes.append(f"{planet} entered {current_row['Sign']}")
            
            # Check for nakshatra change
            if current_row["Nakshatra"] != prev_nakshatra:
                significant_changes.append(f"{planet} entered {current_row['Nakshatra']}")
            
            # Check for significant degree movement (more than 30 minutes)
            current_deg = float(current_row["Degree"].split('°')[0]) + float(current_row["Degree"].split('°')[1].split("'")[0])/60
            prev_deg = float(prev_degree.split('°')[0]) + float(prev_degree.split('°')[1].split("'")[0])/60
            
            if abs(current_deg - prev_deg) > 0.5:  # More than 30 minutes movement
                significant_changes.append(f"{planet} moved to {current_row['Degree']}")
        else:
            # Planet wasn't in previous data (shouldn't happen but just in case)
            significant_changes.append(f"{planet} in {current_row['Sign']} {current_row['Degree']}")
    
    return significant_changes if significant_changes else ["No significant changes"]

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
    start_time = st.time_input("Start Time (IST)", datetime(2025, 7, 29, 9, 15).time())  # Market open time
    end_date = st.date_input("End Date", datetime(2025, 7, 29))
    end_time = st.time_input("End Time (IST)", datetime(2025, 7, 29, 15, 30).time())  # Market close time
    
    if st.button("Search"):
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        if start_datetime > end_datetime:
            st.error("End datetime must be after start datetime.")
        else:
            timeline = []
            current_time = start_datetime
            previous_positions = None
            
            while current_time <= end_datetime:
                positions = get_planetary_positions(current_time)
                aspects = get_aspects(positions)
                signal, color, bull_score, bear_score = get_trading_signal(aspects)
                
                # Get only significant transits (changes from previous time)
                significant_transits = get_significant_transits(positions, previous_positions)
                
                # Format active aspects for display
                active_aspects = []
                if not aspects.empty:
                    for _, aspect in aspects.iterrows():
                        active_aspects.append(f"{aspect['Planet1']}-{aspect['Planet2']}: {aspect['Aspect']}")
                
                timeline.append({
                    "DateTime": current_time.strftime("%Y-%m-%d %H:%M IST"),
                    "Significant Transits": ", ".join(significant_transits),
                    "Active Aspects": ", ".join(active_aspects),
                    "Signal": signal,
                    "Bullish Score": bull_score,
                    "Bearish Score": bear_score,
                    "Color": color
                })
                
                # Update previous_positions for next iteration
                previous_positions = positions.copy()
                current_time += timedelta(minutes=15)  # 15-minute intraday intervals
            
            timeline_df = pd.DataFrame(timeline)
            
            # Create a copy of the DataFrame for display
            display_df = timeline_df.drop(columns=['Color'])
            
            # Define a function to map signal values to colors
            def color_signal(val):
                if val == "Strong Buy":
                    return 'color: green'
                elif val == "Buy":
                    return 'color: lightgreen'
                elif val == "Strong Sell":
                    return 'color: red'
                elif val == "Sell":
                    return 'color: lightcoral'
                else:
                    return 'color: gray'
            
            # Apply the styling
            styled_df = display_df.style.applymap(color_signal, subset=['Signal'])
            
            # Display the dataframe
            st.dataframe(styled_df)
            
            # Add a chart showing signal strength over time
            st.subheader("Signal Strength Over Time")
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=timeline_df["DateTime"],
                y=timeline_df["Bullish Score"],
                mode='lines+markers',
                name='Bullish Score',
                line=dict(color='green')
            ))
            
            fig.add_trace(go.Scatter(
                x=timeline_df["DateTime"],
                y=timeline_df["Bearish Score"],
                mode='lines+markers',
                name='Bearish Score',
                line=dict(color='red')
            ))
            
            fig.update_layout(
                title=f'Bullish vs Bearish Score for {symbol}',
                xaxis_title='Time',
                yaxis_title='Score',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)

# Instructions
st.markdown("""
### Instructions
1. Install dependencies: `pip install -r requirements.txt` and `pip install pyswisseph`.
2. Run the app: `streamlit run script.py`.
3. Use the 'Planetary Report' tab to view monthly transits with dates.
4. Use the 'Stock Search' tab to input a stock symbol, date range with times, and analyze the intraday timeline.
5. Ensure Swiss Ephemeris data files are installed[](https://pyswisseph.readthedocs.io/en/latest/installation.html).
""")
