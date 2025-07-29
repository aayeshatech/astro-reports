import streamlit as st
import swisseph as swe
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import uuid

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

# Simulated Almanac Data Fetch (Placeholder)
def fetch_almanac_data(date):
    # Simulated data for July 30, 2025 (replace with API call if available)
    if date.date() == datetime(2025, 7, 30).date():
        return {
            "positions": {
                "Sun": {"sign": "Leo", "degree": 7.5, "nakshatra": "Magha", "retro": False},
                "Moon": {"sign": "Virgo", "degree": 15.3, "nakshatra": "Hasta", "retro": False},
                "Mars": {"sign": "Taurus", "degree": 22.1, "nakshatra": "Rohini", "retro": False},
                "Jupiter": {"sign": "Cancer", "degree": 18.9, "nakshatra": "Pushya", "retro": True},
                "Venus": {"sign": "Gemini", "degree": 3.5, "nakshatra": "Mrigashira", "retro": False},
                "Saturn": {"sign": "Pisces", "degree": 10.2, "nakshatra": "Uttara Bhadrapada", "retro": True},
                "Rahu": {"sign": "Aquarius", "degree": 25.7, "nakshatra": "Purva Bhadrapada", "retro": False},
                "Ketu": {"sign": "Leo", "degree": 25.7, "nakshatra": "Purva Phalguni", "retro": False}
            },
            "aspects": [
                {"planet1": "Moon", "planet2": "Venus", "aspect": "Sextile", "degree": 58.2},
                {"planet1": "Mars", "planet2": "Saturn", "aspect": "Square", "degree": 88.1}
            ]
        }
    return None

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

# Function to calculate planetary positions with intraday updates
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
    almanac_data = fetch_almanac_data(date_time)
    for planet, pid in planets.items():
        if almanac_data and planet in almanac_data["positions"]:
            pos = almanac_data["positions"][planet]
            lon_sid = (zodiac_signs.index(pos["sign"]) * 30 + pos["degree"]) % 360
            sign = pos["sign"]
            nak = pos["nakshatra"]
            pada = 1  # Simplified for almanac data
            is_retro = pos["retro"]
            # Calculate house for almanac data
            _, house = get_zodiac_house(lon_sid)
        else:
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
            "Retrograde": "Yes" if is_retro else "No" if is_retro != "N/A" else "N/A",
            "Date": date_time.strftime("%Y-%m-%d %H:%M IST")
        })
    return pd.DataFrame(positions)

# Function to calculate aspects with almanac data
def get_aspects(positions, previous_aspects=None):
    aspects = []
    planets = positions["Planet"].tolist()
    degrees = positions["Degree"].apply(lambda x: float(x.split('°')[0]) + float(x.split('°')[1].split("'")[0])/60)
    # Convert string date to datetime object
    date_str = positions.iloc[0]["Date"]
    date_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M IST")
    almanac_data = fetch_almanac_data(date_time)
    
    if almanac_data and "aspects" in almanac_data:
        for aspect in almanac_data["aspects"]:
            aspects.append({
                "Planet1": aspect["planet1"],
                "Planet2": aspect["planet2"],
                "Aspect": aspect["aspect"],
                "Degree": aspect["degree"],
                "Weight": (planet_weights.get(aspect["planet1"], 1.0) + planet_weights.get(aspect["planet2"], 1.0)) / 2
            })
    else:
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
                
                weight = (planet_weights.get(p1, 1.0) + planet_weights.get(p2, 1.0)) / 2
                
                if diff < 3:
                    aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Conjunction", 
                                   "Degree": f"{diff:.2f}°", "Weight": weight})
                elif 57 < diff < 63:
                    aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Sextile", 
                                   "Degree": f"{diff:.2f}°", "Weight": weight})
                elif 87 < diff < 93:
                    aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Square", 
                                   "Degree": f"{diff:.2f}°", "Weight": weight})
                elif 117 < diff < 123:
                    aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Trine", 
                                   "Degree": f"{diff:.2f}°", "Weight": weight})
                elif 177 < diff < 183:
                    aspects.append({"Planet1": p1, "Planet2": p2, "Aspect": "Opposition", 
                                   "Degree": f"{diff:.2f}°", "Weight": weight})
    
    current_aspects = pd.DataFrame(aspects)
    new_aspects = []
    dissolved_aspects = []
    
    if previous_aspects is not None:
        current_keys = set((row["Planet1"], row["Planet2"], row["Aspect"]) for _, row in current_aspects.iterrows())
        prev_keys = set((row["Planet1"], row["Planet2"], row["Aspect"]) for _, row in previous_aspects.iterrows())
        
        new_aspects = [row for _, row in current_aspects.iterrows() if (row["Planet1"], row["Planet2"], row["Aspect"]) in (current_keys - prev_keys)]
        dissolved_aspects = [row for _, row in previous_aspects.iterrows() if (row["Planet1"], row["Planet2"], row["Aspect"]) in (prev_keys - current_keys)]
    
    return current_aspects, new_aspects, dissolved_aspects

# Improved function to determine trading signals with swing logic
def get_trading_signal(aspects, new_aspects, dissolved_aspects, previous_signal="Neutral"):
    try:
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
                if aspect["Planet1"] in ["Jupiter", "Venus"] or aspect["Planet2"] in ["Jupiter", "Venus"]:
                    bullish_score += weight * 0.8
                elif aspect["Planet1"] in ["Mars", "Saturn", "Rahu", "Ketu"] or aspect["Planet2"] in ["Mars", "Saturn", "Rahu", "Ketu"]:
                    bearish_score += weight * 0.8
        
        # Adjust scores based on new and dissolved aspects for swing signals
        for aspect in new_aspects:
            weight = aspect.get("Weight", 0)
            if aspect["Aspect"] in ["Trine", "Sextile"]:
                bullish_score += weight * 1.2  # Boost for new bullish aspect
            elif aspect["Aspect"] in ["Square", "Opposition"]:
                bearish_score += weight * 1.2  # Boost for new bearish aspect
        
        for aspect in dissolved_aspects:
            weight = aspect.get("Weight", 0)
            if aspect["Aspect"] in ["Trine", "Sextile"]:
                bullish_score -= weight * 0.5  # Reduce for dissolved bullish aspect
            elif aspect["Aspect"] in ["Square", "Opposition"]:
                bearish_score -= weight * 0.5  # Reduce for dissolved bearish aspect
        
        # Determine swing signal based on score changes and previous signal
        signal = "Neutral"
        color = "gray"
        if bullish_score > bearish_score * 1.5 or (new_aspects and any(a["Aspect"] in ["Trine", "Sextile"] for a in new_aspects)):
            signal = "Swing Buy"
            color = "lightgreen"
        elif bearish_score > bullish_score * 1.5 or (new_aspects and any(a["Aspect"] in ["Square", "Opposition"] for a in new_aspects)):
            signal = "Swing Sell"
            color = "lightcoral"
        elif bullish_score > bearish_score:
            signal = "Buy"
            color = "lightgreen"
        elif bearish_score > bullish_score:
            signal = "Sell"
            color = "lightcoral"
        
        return signal, color, bullish_score, bearish_score
    except Exception as e:
        st.error(f"Error in get_trading_signal: {str(e)}")
        return "Neutral", "gray", 0, 0

# Function to get significant transits
def get_significant_transits(current_positions, previous_positions=None, reported_transits=None):
    if reported_transits is None:
        reported_transits = set()
    
    if previous_positions is None:
        initial_transits = [f"{row['Planet']} in {row['Sign']} {row['Degree']}" for _, row in current_positions.iterrows()]
        return initial_transits, set(), reported_transits.union(set(initial_transits))
    
    significant_changes = []
    nakshatra_changes = []
    
    for _, current_row in current_positions.iterrows():
        planet = current_row["Planet"]
        previous_row = previous_positions[previous_positions["Planet"] == planet]
        
        if not previous_row.empty:
            prev_sign = previous_row.iloc[0]["Sign"]
            prev_degree = previous_row.iloc[0]["Degree"]
            prev_nakshatra = previous_row.iloc[0]["Nakshatra"]
            
            if current_row["Sign"] != prev_sign:
                change = f"{planet} entered {current_row['Sign']}"
                if change not in reported_transits:
                    significant_changes.append(change)
                    reported_transits.add(change)
            
            if current_row["Nakshatra"] != prev_nakshatra:
                change = f"{planet} entered {current_row['Nakshatra']}"
                if change not in reported_transits:
                    significant_changes.append(change)
                    reported_transits.add(change)
                    nakshatra_changes.append(planet)
            
            try:
                current_parts = current_row["Degree"].split('°')
                if len(current_parts) != 2:
                    raise ValueError(f"Invalid degree format for {planet}: {current_row['Degree']}")
                deg, min_str = current_parts
                min_parts = min_str.split("'")
                if len(min_parts) != 2:
                    raise ValueError(f"Invalid minute format for {planet}: {min_str}")
                current_deg = float(deg) + float(min_parts[0])/60
                
                prev_parts = prev_degree.split('°')
                if len(prev_parts) != 2:
                    raise ValueError(f"Invalid degree format for {planet}: {prev_degree}")
                prev_deg_val, prev_min_str = prev_parts
                prev_min_parts = prev_min_str.split("'")
                if len(prev_min_parts) != 2:
                    raise ValueError(f"Invalid minute format for {planet}: {prev_min_str}")
                prev_deg = float(prev_deg_val) + float(prev_min_parts[0])/60
                
                if abs(current_deg - prev_deg) > 0.5:
                    change = f"{planet} moved to {current_row['Degree']}"
                    if change not in reported_transits:
                        significant_changes.append(change)
                        reported_transits.add(change)
            except (ValueError, IndexError) as e:
                st.warning(f"Error parsing degrees for {planet}: {str(e)}. Skipping degree comparison.")
                significant_changes.append(f"{planet} degree parsing failed")
        else:
            change = f"{planet} in {current_row['Sign']} {current_row['Degree']}"
            if change not in reported_transits:
                significant_changes.append(change)
                reported_transits.add(change)
    
    return significant_changes if significant_changes else [], nakshatra_changes, reported_transits

# Streamlit app
st.set_page_config(layout="wide")
st.title("Astro Market Analyzer")

st.markdown("""
    <style>
    .stDataFrame {
        width: 100%;
        max-width: 1200px;
    }
    .highlight-nakshatra {
        background-color: #FFFF99 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["Planetary Report", "Stock Search"])

# Planetary Report Tab
with tab1:
    st.header("Planetary Transits Report")
    year = datetime.now().year
    
    def display_monthly_transits(month, transits, title):
        st.subheader(title)
        monthly_data = []
        previous_positions = None
        for day, positions in enumerate(transits, 1):
            if day == 1:
                for _, row in positions.iterrows():
                    monthly_data.append({
                        "Date": row["Date"].split(" ")[0],
                        "Planet": row["Planet"],
                        "Sign": row["Sign"],
                        "Degree": row["Degree"],
                        "House": row["House"],
                        "Nakshatra": row["Nakshatra"],
                        "Pada": row["Pada"],
                        "Retrograde": row["Retrograde"]
                    })
            _, nakshatra_changes, _ = get_significant_transits(positions, previous_positions)
            if nakshatra_changes:
                for planet in nakshatra_changes:
                    idx = positions[positions["Planet"] == planet].index[0]
                    monthly_data.append({
                        "Date": positions.iloc[idx]["Date"].split(" ")[0],
                        "Planet": positions.iloc[idx]["Planet"],
                        "Sign": positions.iloc[idx]["Sign"],
                        "Degree": positions.iloc[idx]["Degree"],
                        "House": positions.iloc[idx]["House"],
                        "Nakshatra": positions.iloc[idx]["Nakshatra"],
                        "Pada": positions.iloc[idx]["Pada"],
                        "Retrograde": positions.iloc[idx]["Retrograde"]
                    })
            previous_positions = positions.copy()
        
        monthly_df = pd.DataFrame(monthly_data)
        
        def highlight_nakshatra_changes(s):
            if s["Date"] != f"{year}-{month:02d}-01":
                return ['background-color: #FFFF99'] * len(s)
            return [''] * len(s)
        
        if not monthly_df.empty:
            styled_df = monthly_df.style.apply(highlight_nakshatra_changes, axis=1)
            st.dataframe(styled_df, use_container_width=True)
        
        # Collect aspects with date
        aspect_data = []
        previous_aspects = None
        for day, positions in enumerate(transits, 1):
            current_aspects, _, _ = get_aspects(positions, previous_aspects)
            for _, aspect in current_aspects.iterrows():
                date = positions.iloc[0]["Date"].split(" ")[0]  # Use first position's date
                tendency = "Bullish" if aspect["Aspect"] in ["Trine", "Sextile"] else \
                           "Bearish" if aspect["Aspect"] in ["Square", "Opposition"] else \
                           "Neutral" if aspect["Aspect"] == "Conjunction" and \
                           (aspect["Planet1"] in ["Jupiter", "Venus"] or aspect["Planet2"] in ["Jupiter", "Venus"]) else "Bearish"
                aspect_data.append({
                    "Date": date,
                    "Planet1": aspect["Planet1"],
                    "Planet2": aspect["Planet2"],
                    "Aspect": aspect["Aspect"],
                    "Degree": aspect["Degree"],
                    "Weight": aspect["Weight"],
                    "Bullish or Bearish": tendency
                })
            previous_aspects = current_aspects.copy()
        
        aspects_df = pd.DataFrame(aspect_data)
        if not aspects_df.empty:
            st.subheader(f"{title} Aspects")
            st.dataframe(aspects_df, use_container_width=True)

    # July Transits
    july_transits = []
    for day in range(1, 32):
        try:
            date = datetime(year, 7, day, 9, 0)
            positions = get_planetary_positions(date)
            july_transits.append(positions)
        except ValueError:
            break
    display_monthly_transits(7, july_transits, f"July {year} Transits")

    # August Transits
    aug_transits = []
    for day in range(1, 32):
        try:
            date = datetime(year, 8, day, 9, 0)
            positions = get_planetary_positions(date)
            aug_transits.append(positions)
        except ValueError:
            break
    display_monthly_transits(8, aug_transits, f"August {year} Transits")

# Stock Search Tab
with tab2:
    st.header("Stock Search")
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        with col1:
            symbol = st.text_input("Enter Stock Symbol", "NIFTY")
        with col2:
            start_date = st.date_input("Start Date", datetime(2025, 7, 30))
        with col3:
            start_time = st.time_input("Start Time (IST)", datetime(2025, 7, 30, 9, 15).time())
        with col4:
            end_date = st.date_input("End Date", datetime(2025, 7, 30))
            end_time = st.time_input("End Time (IST)", datetime(2025, 7, 30, 15, 30).time())
    
    if st.button("Search"):
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        if start_datetime > end_datetime:
            st.error("End datetime must be after start datetime.")
        else:
            timeline = []
            previous_positions = None
            previous_aspects = None
            reported_transits = set()
            previous_signal = "Neutral"
            
            current_time = start_datetime
            while current_time <= end_datetime:
                positions = get_planetary_positions(current_time)
                current_aspects, new_aspects, dissolved_aspects = get_aspects(positions, previous_aspects)
                signal, color, bull_score, bearish_score = get_trading_signal(current_aspects, new_aspects, dissolved_aspects, previous_signal)
                
                significant_transits, _, reported_transits = get_significant_transits(positions, previous_positions, reported_transits)
                
                active_aspects = []
                unique_aspects = set()
                for _, aspect in current_aspects.iterrows():
                    aspect_key = f"{aspect['Planet1']}-{aspect['Planet2']}-{aspect['Aspect']}"
                    if aspect_key not in unique_aspects:
                        unique_aspects.add(aspect_key)
                        active_aspects.append(f"{aspect['Planet1']}-{aspect['Planet2']}: {aspect['Aspect']} ({aspect['Degree']})")
                
                transits_display = ", ".join(significant_transits) if significant_transits else "No significant changes" if not timeline else ""
                
                timeline.append({
                    "DateTime": current_time.strftime("%Y-%m-%d %H:%M IST"),
                    "Significant Transits": transits_display,
                    "Active Aspects": ", ".join(active_aspects),
                    "Signal": signal,
                    "Bullish Score": bull_score,
                    "Bearish Score": bearish_score,
                    "Color": color
                })
                
                previous_positions = positions.copy()
                previous_aspects = current_aspects.copy()
                previous_signal = signal
                current_time += timedelta(minutes=15)
            
            timeline_df = pd.DataFrame(timeline)
            
            display_df = timeline_df.drop(columns=['Color'])
            
            def color_signal(val):
                if val == "Swing Buy":
                    return 'color: green'
                elif val == "Buy":
                    return 'color: lightgreen'
                elif val == "Swing Sell":
                    return 'color: red'
                elif val == "Sell":
                    return 'color: lightcoral'
                else:
                    return 'color: gray'
            
            styled_df = display_df.style.applymap(color_signal, subset=['Signal'])
            st.dataframe(styled_df, use_container_width=True)
            
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
                hovermode='x unified',
                width=1200
            )
            
            st.plotly_chart(fig, use_container_width=True)

# Instructions
st.markdown("""
### Instructions
1. Install dependencies: `pip install -r requirements.txt` and `pip install pyswisseph`.
2. Run the app: `streamlit run astro-reports.py`.
3. Use the 'Planetary Report' tab to view monthly transits and detailed aspects with date, planets, aspect, degree, weight, and bullish/bearish tendency.
4. Use the 'Stock Search' tab to input a stock symbol, date range with times, and analyze the intraday timeline with updated planetary positions and astro aspect-based signals.
5. Ensure Swiss Ephemeris data files are installed (see https://pyswisseph.readthedocs.io/en/latest/installation.html).
""")
