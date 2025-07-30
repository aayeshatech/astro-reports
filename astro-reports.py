import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import json
import time

# Try to import swisseph, fallback to simulation if not available
try:
    import swisseph as swe
    SWISSEPH_AVAILABLE = True
except ImportError:
    SWISSEPH_AVAILABLE = False
    st.warning("⚠️ Swiss Ephemeris not installed. Using simulation mode.")

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

# Enhanced planet weights for aspect strength
planet_weights = {
    "Sun": 2.0, "Moon": 1.8, "Mars": 1.5, "Mercury": 1.2,
    "Jupiter": 2.2, "Venus": 1.6, "Saturn": 1.8,
    "Rahu": 1.4, "Ketu": 1.4, "North Node": 1.4, "South Node": 1.4
}

# Aspect strength multipliers
aspect_strength = {
    "Conjunction": 1.0, "Sextile": 0.8, "Square": 1.2, "Trine": 1.0,
    "Opposition": 1.3, "Semisextile": 0.4, "Semisquare": 0.6,
    "Sesquiquadrate": 0.6, "Quincunx": 0.5, "Inconjunct": 0.5
}

# Simulation data for when APIs are not available
def get_simulation_data(date_time):
    """
    Generate realistic planetary positions for simulation mode
    """
    # Base positions for July 30, 2025 (realistic approximations)
    base_positions = {
        "Sun": {"longitude": 127.5, "sign": "Leo", "nakshatra": "Magha", "retrograde": False},
        "Moon": {"longitude": 165.3, "sign": "Virgo", "nakshatra": "Hasta", "retrograde": False},
        "Mars": {"longitude": 52.1, "sign": "Taurus", "nakshatra": "Rohini", "retrograde": False},
        "Mercury": {"longitude": 115.8, "sign": "Cancer", "nakshatra": "Pushya", "retrograde": False},
        "Jupiter": {"longitude": 108.9, "sign": "Cancer", "nakshatra": "Pushya", "retrograde": True},
        "Venus": {"longitude": 63.5, "sign": "Gemini", "nakshatra": "Punarvasu", "retrograde": False},
        "Saturn": {"longitude": 340.2, "sign": "Pisces", "nakshatra": "Uttara Bhadrapada", "retrograde": True},
        "Rahu": {"longitude": 325.7, "sign": "Pisces", "nakshatra": "Uttara Bhadrapada", "retrograde": True},
        "Ketu": {"longitude": 145.7, "sign": "Virgo", "nakshatra": "Uttara Phalguni", "retrograde": True}
    }
    
    # Calculate time difference from base date
    base_date = datetime(2025, 7, 30, 12, 0, 0)
    time_diff = (date_time - base_date).total_seconds() / 3600  # hours
    
    # Planetary speeds (degrees per hour - approximations)
    speeds = {
        "Sun": 0.041667, "Moon": 0.5416, "Mercury": 0.083, "Venus": 0.046,
        "Mars": 0.024, "Jupiter": 0.0033, "Saturn": 0.001389,
        "Rahu": -0.00217, "Ketu": -0.00217  # Retrograde
    }
    
    # Update positions based on time
    updated_positions = {}
    for planet, data in base_positions.items():
        new_longitude = (data["longitude"] + speeds.get(planet, 0) * time_diff) % 360
        updated_positions[planet] = {
            "longitude": new_longitude,
            "retrograde": data["retrograde"]
        }
    
    return updated_positions

# Cache for API responses to avoid repeated calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_astronomics_data(date_str, time_str=None):
    """
    Attempt to fetch astronomical data from astronomics.ai API
    """
    try:
        base_url = "https://data.astronomics.ai/almanac/"
        
        # Format the request URL
        if time_str:
            url = f"{base_url}?date={date_str}&time={time_str}"
        else:
            url = f"{base_url}?date={date_str}"
        
        # Headers for the API request
        headers = {
            'User-Agent': 'Astro-Market-Analyzer/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Make the API request with timeout
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data, "API"
        else:
            return None, f"API_ERROR_{response.status_code}"
            
    except requests.exceptions.Timeout:
        return None, "TIMEOUT"
    except requests.exceptions.ConnectionError:
        return None, "CONNECTION_ERROR"
    except requests.exceptions.RequestException:
        return None, "REQUEST_ERROR"
    except json.JSONDecodeError:
        return None, "JSON_ERROR"
    except Exception as e:
        return None, f"UNKNOWN_ERROR_{str(e)[:50]}"

def get_nakshatra_pada(degree):
    """Calculate Nakshatra and Pada from longitude"""
    for nak, start, end in nakshatras:
        if start <= degree < end:
            pada = int((degree - start) // (13+20/60 / 4)) + 1
            return nak, pada
    return "Unknown", 0

def get_zodiac_house(degree):
    """Get zodiac sign and house from longitude"""
    sign_index = int(degree // 30) % 12
    house_index = int(degree // 30) % 12
    return zodiac_signs[sign_index], houses[house_index]

def convert_degree_to_dms(degree):
    """Convert decimal degree to degrees, minutes, seconds format"""
    degree_in_sign = degree % 30
    degree_int = int(degree_in_sign)
    minute_int = int((degree_in_sign - degree_int) * 60)
    second_int = int(((degree_in_sign - degree_int) * 60 - minute_int) * 60)
    return f"{degree_int}° {minute_int}' {second_int}\""

def get_planetary_positions_swisseph(date_time):
    """
    Calculate planetary positions using Swiss Ephemeris
    """
    if not SWISSEPH_AVAILABLE:
        return pd.DataFrame()
    
    try:
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
            try:
                result = swe.calc_ut(jd, pid)
                lon_trop = result[0][0]
                lon_sid = (lon_trop - ayanamsa) % 360
                
                if planet == "Ketu":
                    lon_sid = (lon_sid + 180) % 360
                
                sign, house = get_zodiac_house(lon_sid)
                nak, pada = get_nakshatra_pada(lon_sid)
                
                # Check retrograde status
                is_retro = "No"
                if planet not in ["Rahu", "Ketu"] and len(result[0]) > 3:
                    is_retro = "Yes" if result[0][3] < 0 else "No"
                elif planet in ["Rahu", "Ketu"]:
                    is_retro = "Yes"
                
                degree_formatted = convert_degree_to_dms(lon_sid)
                
                positions.append({
                    "Planet": planet,
                    "Sign": sign,
                    "Degree": degree_formatted,
                    "Full_Degree": lon_sid,
                    "House": house,
                    "Nakshatra": nak,
                    "Pada": pada,
                    "Retrograde": is_retro,
                    "Date": date_time.strftime("%Y-%m-%d %H:%M:%S IST"),
                    "Source": "SwissEph"
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(positions)
        
    except Exception as e:
        return pd.DataFrame()

def get_planetary_positions_simulation(date_time):
    """
    Get planetary positions using simulation data
    """
    try:
        sim_data = get_simulation_data(date_time)
        positions = []
        
        for planet, data in sim_data.items():
            longitude = data["longitude"]
            sign, house = get_zodiac_house(longitude)
            nak, pada = get_nakshatra_pada(longitude)
            is_retro = "Yes" if data["retrograde"] else "No"
            degree_formatted = convert_degree_to_dms(longitude)
            
            positions.append({
                "Planet": planet,
                "Sign": sign,
                "Degree": degree_formatted,
                "Full_Degree": longitude,
                "House": house,
                "Nakshatra": nak,
                "Pada": pada,
                "Retrograde": is_retro,
                "Date": date_time.strftime("%Y-%m-%d %H:%M:%S IST"),
                "Source": "Simulation"
            })
        
        return pd.DataFrame(positions)
        
    except Exception as e:
        st.error(f"Error in simulation: {str(e)}")
        return pd.DataFrame()

def get_planetary_positions(date_time, data_source="auto"):
    """
    Get planetary positions with fallback priority:
    1. Astronomics.ai API (if available)
    2. Swiss Ephemeris (if installed)
    3. Simulation mode
    """
    positions = pd.DataFrame()
    source_used = "None"
    
    # Try API first if auto mode or API specifically requested
    if data_source in ["auto", "api"]:
        date_str = date_time.strftime("%Y-%m-%d")
        time_str = date_time.strftime("%H:%M:%S")
        api_data, api_status = fetch_astronomics_data(date_str, time_str)
        
        if api_data and api_status == "API":
            # TODO: Parse API data (would need actual API response structure)
            source_used = "API"
        else:
            if data_source == "api":
                st.warning(f"API failed: {api_status}")
    
    # Try Swiss Ephemeris if API failed and SwissEph is available
    if positions.empty and data_source in ["auto", "swisseph"] and SWISSEPH_AVAILABLE:
        positions = get_planetary_positions_swisseph(date_time)
        if not positions.empty:
            source_used = "SwissEph"
    
    # Fall back to simulation
    if positions.empty:
        positions = get_planetary_positions_simulation(date_time)
        source_used = "Simulation"
    
    return positions, source_used

def get_aspects(positions):
    """Calculate aspects between planets"""
    if positions.empty:
        return pd.DataFrame(), []
    
    aspects = []
    planets = positions["Planet"].tolist()
    full_degrees = positions["Full_Degree"].tolist()
    
    # Define aspect angles with orbs
    aspect_config = {
        0: ("Conjunction", 2.0),
        60: ("Sextile", 2.0),
        90: ("Square", 2.0),
        120: ("Trine", 2.0),
        180: ("Opposition", 2.0),
        30: ("Semisextile", 1.0),
        45: ("Semisquare", 1.0),
        135: ("Sesquiquadrate", 1.0),
        150: ("Quincunx", 1.0)
    }
    
    for i, p1 in enumerate(planets):
        for j, p2 in enumerate(planets[i+1:], start=i+1):
            deg1 = full_degrees[i]
            deg2 = full_degrees[j]
            diff = abs(deg2 - deg1)
            if diff > 180:
                diff = 360 - diff
            
            for angle, (aspect_name, orb) in aspect_config.items():
                if abs(diff - angle) <= orb:
                    weight = (planet_weights.get(p1, 1.0) + planet_weights.get(p2, 1.0)) / 2
                    weight *= aspect_strength.get(aspect_name, 1.0)
                    
                    # Determine tendency
                    if aspect_name in ["Sextile", "Trine"]:
                        tendency = "Bullish"
                        if p1 in ["Jupiter", "Venus"] or p2 in ["Jupiter", "Venus"]:
                            weight *= 1.3
                    elif aspect_name in ["Square", "Opposition"]:
                        tendency = "Bearish"
                        if p1 in ["Mars", "Saturn"] or p2 in ["Mars", "Saturn"]:
                            weight *= 1.3
                    elif aspect_name == "Conjunction":
                        if (p1 in ["Jupiter", "Venus", "Moon"] or p2 in ["Jupiter", "Venus", "Moon"]):
                            tendency = "Bullish"
                            weight *= 1.1
                        elif (p1 in ["Mars", "Saturn", "Rahu", "Ketu"] or p2 in ["Mars", "Saturn", "Rahu", "Ketu"]):
                            tendency = "Bearish"
                            weight *= 1.1
                        else:
                            tendency = "Neutral"
                    else:
                        tendency = "Neutral"
                        weight *= 0.7
                    
                    aspects.append({
                        "Planet1": p1,
                        "Planet2": p2,
                        "Aspect": aspect_name,
                        "Exact_Degree": f"{diff:.2f}°",
                        "Orb": f"{abs(diff - angle):.2f}°",
                        "Weight": round(weight, 2),
                        "Tendency": tendency,
                        "Strength": "Strong" if abs(diff - angle) <= orb/2 else "Moderate"
                    })
                    break
    
    return pd.DataFrame(aspects), aspects

def get_enhanced_trading_signal(aspects_df, new_aspects=None, dissolved_aspects=None):
    """Calculate enhanced trading signal based on aspects"""
    if aspects_df.empty:
        return "Neutral", "gray", 0, 0, "No aspects"
    
    bullish_score = 0
    bearish_score = 0
    signal_details = []
    
    # Calculate base scores
    for _, aspect in aspects_df.iterrows():
        weight = aspect["Weight"]
        strength_multiplier = 1.5 if aspect["Strength"] == "Strong" else 1.0
        
        if aspect["Tendency"] == "Bullish":
            bullish_score += weight * strength_multiplier
            signal_details.append(f"+{weight:.1f} ({aspect['Planet1']}-{aspect['Planet2']} {aspect['Aspect']})")
        elif aspect["Tendency"] == "Bearish":
            bearish_score += weight * strength_multiplier
            signal_details.append(f"-{weight:.1f} ({aspect['Planet1']}-{aspect['Planet2']} {aspect['Aspect']})")
    
    # Bonus for new strong aspects
    if new_aspects:
        for aspect in new_aspects:
            if aspect.get("Strength") == "Strong":
                if aspect["Tendency"] == "Bullish":
                    bullish_score += aspect["Weight"] * 0.5
                elif aspect["Tendency"] == "Bearish":
                    bearish_score += aspect["Weight"] * 0.5
    
    # Determine signal strength
    total_score = bullish_score + bearish_score
    net_score = bullish_score - bearish_score
    
    if total_score == 0:
        signal = "Neutral"
        color = "gray"
    elif abs(net_score) / total_score > 0.6:  # Strong signal threshold
        if net_score > 0:
            signal = "Strong Buy" if net_score / total_score > 0.8 else "Buy"
            color = "darkgreen" if signal == "Strong Buy" else "lightgreen"
        else:
            signal = "Strong Sell" if abs(net_score) / total_score > 0.8 else "Sell"
            color = "darkred" if signal == "Strong Sell" else "lightcoral"
    elif abs(net_score) / total_score > 0.3:  # Moderate signal
        if net_score > 0:
            signal = "Buy"
            color = "lightgreen"
        else:
            signal = "Sell"
            color = "lightcoral"
    else:
        signal = "Neutral"
        color = "gray"
    
    details = "; ".join(signal_details[:5])  # Limit details
    return signal, color, round(bullish_score, 2), round(bearish_score, 2), details

def detect_significant_transits(current_positions, previous_positions=None):
    """Detect significant planetary transits"""
    if previous_positions is None or previous_positions.empty:
        return []
    
    transits = []
    
    for _, current_row in current_positions.iterrows():
        planet = current_row["Planet"]
        prev_row = previous_positions[previous_positions["Planet"] == planet]
        
        if not prev_row.empty:
            prev_row = prev_row.iloc[0]
            
            # Sign change
            if current_row["Sign"] != prev_row["Sign"]:
                transits.append(f"{planet}: {prev_row['Sign']} → {current_row['Sign']}")
            
            # Nakshatra change
            elif current_row["Nakshatra"] != prev_row["Nakshatra"]:
                transits.append(f"{planet}: {prev_row['Nakshatra']} → {current_row['Nakshatra']}")
            
            # Degree movement (significant)
            else:
                deg_diff = abs(current_row["Full_Degree"] - prev_row["Full_Degree"])
                if deg_diff > 1.0:  # More than 1 degree movement
                    transits.append(f"{planet}: {deg_diff:.1f}° movement")
    
    return transits

# Streamlit app
st.set_page_config(layout="wide", page_title="Enhanced Astro Market Analyzer - Multi-Source")
st.title("🌟 Enhanced Astro Market Analyzer")
st.subheader("🔄 Multi-Source Data Integration")

# Custom CSS for better styling
st.markdown("""
    <style>
    .stDataFrame {
        width: 100%;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .signal-strong-buy { background-color: #00ff00; color: black; }
    .signal-buy { background-color: #90ee90; color: black; }
    .signal-sell { background-color: #ffcccb; color: black; }
    .signal-strong-sell { background-color: #ff0000; color: white; }
    .signal-neutral { background-color: #d3d3d3; color: black; }
    .source-api { background-color: #e7f3ff; color: #0066cc; }
    .source-swisseph { background-color: #f0f8e7; color: #2d5016; }
    .source-simulation { background-color: #fff3cd; color: #856404; }
    </style>
""", unsafe_allow_html=True)

# Data Source Selection
st.sidebar.header("📊 Data Source Settings")
with st.sidebar:
    data_source = st.selectbox(
        "Primary Data Source",
        ["auto", "api", "swisseph", "simulation"],
        format_func=lambda x: {
            "auto": "🔄 Auto (API → SwissEph → Simulation)",
            "api": "🌐 Astronomics.ai API Only",
            "swisseph": "🔭 Swiss Ephemeris Only",
            "simulation": "🎲 Simulation Mode Only"
        }[x],
        help="Choose your preferred data source or let the system auto-select"
    )
    
    # Display data source status
    st.subheader("📋 Source Status")
    
    # API Status
    if st.button("Test API", help="Test astronomics.ai connection"):
        with st.spinner("Testing API..."):
            test_data, status = fetch_astronomics_data("2025-07-30")
            if status == "API":
                st.success("✅ API Available")
            else:
                st.error(f"❌ API Failed: {status}")
    
    # Swiss Ephemeris Status
    if SWISSEPH_AVAILABLE:
        st.success("✅ Swiss Ephemeris Available")
    else:
        st.warning("⚠️ Swiss Ephemeris Not Installed")
    
    # Simulation always available
    st.info("ℹ️ Simulation Mode Always Available")

# Tabs
tab1, tab2 = st.tabs(["📊 Planetary Report", "🔍 Enhanced Stock Analysis"])

# Planetary Report Tab
with tab1:
    st.header("Current Planetary Positions")
    
    # Display current planetary positions
    current_time = datetime.now()
    with st.spinner("Fetching current planetary data..."):
        current_positions, source_used = get_planetary_positions(current_time, data_source)
        
        if not current_positions.empty:
            # Source indicator
            source_colors = {
                "API": "🌐", "SwissEph": "🔭", "Simulation": "🎲", "None": "❌"
            }
            st.success(f"{source_colors.get(source_used, '❓')} Data Source: **{source_used}** | Time: {current_time.strftime('%Y-%m-%d %H:%M')} IST")
            
            # Display positions
            display_positions = current_positions.drop(columns=['Full_Degree'])
            st.dataframe(display_positions, use_container_width=True)
            
            # Current aspects
            current_aspects_df, _ = get_aspects(current_positions)
            if not current_aspects_df.empty:
                st.subheader("Current Active Aspects")
                st.dataframe(current_aspects_df, use_container_width=True)
                
                # Quick signal analysis
                signal, color, bull_score, bear_score, details = get_enhanced_trading_signal(current_aspects_df)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Current Signal", signal)
                with col2:
                    st.metric("Bullish Score", f"{bull_score:.2f}")
                with col3:
                    st.metric("Bearish Score", f"{bear_score:.2f}")
                with col4:
                    st.metric("Net Score", f"{bull_score - bear_score:.2f}")
            else:
                st.info("No significant aspects currently active")
        else:
            st.error("❌ Failed to fetch planetary data from all sources")

# Enhanced Stock Search Tab
with tab2:
    st.header("🚀 Enhanced Stock Analysis")
    
    # Input section with improved layout
    with st.container():
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📈 Stock & Time Settings")
            symbol = st.text_input("Stock Symbol", "NIFTY", help="Enter the stock symbol you want to analyze")
            
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                start_date = st.date_input("Start Date", datetime(2025, 7, 30))
                start_time = st.time_input("Start Time (IST)", datetime(2025, 7, 30, 9, 15).time())
            with date_col2:
                end_date = st.date_input("End Date", datetime(2025, 7, 30))
                end_time = st.time_input("End Time (IST)", datetime(2025, 7, 30, 15, 30).time())
        
        with col2:
            st.subheader("⚙️ Analysis Settings")
            time_interval = st.selectbox("Time Interval", 
                                       ["15 minutes", "30 minutes", "1 hour", "2 hours"], 
                                       index=0)
            
            show_details = st.checkbox("Show Detailed Aspects", True)
            show_transits = st.checkbox("Show Transit Changes", True)
            show_source_info = st.checkbox("Show Data Source Info", True)
            
            interval_map = {"15 minutes": 15, "30 minutes": 30, "1 hour": 60, "2 hours": 120}
            interval_minutes = interval_map[time_interval]
    
    if st.button("🔮 Analyze Stock", type="primary"):
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        
        if start_datetime >= end_datetime:
            st.error("❌ End datetime must be after start datetime.")
        else:
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            source_text = st.empty()
            
            # Calculate timeline
            timeline = []
            previous_positions = None
            previous_aspects_df = pd.DataFrame()
            source_stats = {"API": 0, "SwissEph": 0, "Simulation": 0, "None": 0}
            
            total_intervals = int((end_datetime - start_datetime).total_seconds() / (interval_minutes * 60))
            current_time = start_datetime
            interval_count = 0
            
            while current_time <= end_datetime:
                # Update progress
                progress = min(interval_count / max(total_intervals, 1), 1.0)
                progress_bar.progress(progress)
                status_text.text(f"Analyzing: {current_time.strftime('%Y-%m-%d %H:%M')} ({interval_count + 1}/{total_intervals + 1})")
                
                if show_source_info:
                    source_text.text(f"Sources used - API: {source_stats['API']} | SwissEph: {source_stats['SwissEph']} | Simulation: {source_stats['Simulation']}")
                
                # Get current positions
                positions, source_used = get_planetary_positions(current_time, data_source)
                source_stats[source_used] = source_stats.get(source_used, 0) + 1
                
                if not positions.empty:
                    current_aspects_df, aspects_list = get_aspects(positions)
                    
                    # Detect new and dissolved aspects
                    new_aspects = []
                    dissolved_aspects = []
                    
                    if not previous_aspects_df.empty:
                        prev_keys = set((row["Planet1"], row["Planet2"], row["Aspect"]) for _, row in previous_aspects_df.iterrows())
                        curr_keys = set((row["Planet1"], row["Planet2"], row["Aspect"]) for _, row in current_aspects_df.iterrows())
                        
                        new_aspect_keys = curr_keys - prev_keys
                        dissolved_aspect_keys = prev_keys - curr_keys
                        
                        new_aspects = [row for _, row in current_aspects_df.iterrows() 
                                     if (row["Planet1"], row["Planet2"], row["Aspect"]) in new_aspect_keys]
                        dissolved_aspects = [row for _, row in previous_aspects_df.iterrows() 
                                           if (row["Planet1"], row["Planet2"], row["Aspect"]) in dissolved_aspect_keys]
                    
                    # Get trading signal
                    signal, color, bull_score, bear_score, signal_details = get_enhanced_trading_signal(
                        current_aspects_df, new_aspects, dissolved_aspects
                    )
                    
                    # Detect transits
                    transits = detect_significant_transits(positions, previous_positions) if show_transits else []
                    
                    # Count aspects by type
                    aspect_counts = current_aspects_df["Tendency"].value_counts()
                    
                    timeline.append({
                        "DateTime": current_time.strftime("%Y-%m-%d %H:%M"),
                        "Day": current_time.strftime("%A"),
                        "Source": source_used,
                        "Transits": "; ".join(transits) if transits else "None",
                        "Active_Aspects": len(current_aspects_df),
                        "Bullish_Aspects": aspect_counts.get("Bullish", 0),
                        "Bearish_Aspects": aspect_counts.get("Bearish", 0),
                        "Signal": signal,
                        "Bullish_Score": bull_score,
                        "Bearish_Score": bear_score,
                        "Net_Score": bull_score - bear_score,
                        "Signal_Details": signal_details if show_details else "",
                        "Color": color
                    })
                    
                    previous_positions = positions.copy()
                    previous_aspects_df = current_aspects_df.copy()
                else:
                    # Add error entry
                    timeline.append({
                        "DateTime": current_time.strftime("%Y-%m-%d %H:%M"),
                        "Day": current_time.strftime("%A"),
                        "Source": "Error",
                        "Transits": "Data Error",
                        "Active_Aspects": 0,
                        "Bullish_Aspects": 0,
                        "Bearish_Aspects": 0,
                        "Signal": "Error",
                        "Bullish_Score": 0,
                        "Bearish_Score": 0,
                        "Net_Score": 0,
                        "Signal_Details": "Failed to fetch data",
                        "Color": "red"
                    })
                
                current_time += timedelta(minutes=interval_minutes)
                interval_count += 1
                
                # Small delay for API calls
                if data_source in ["auto", "api"]:
                    time.sleep(0.2)
            
            progress_bar.progress(1.0)
            status_text.text("✅ Analysis Complete!")
            
            # Data Source Summary
            total_calls = sum(source_stats.values())
            if total_calls > 0:
                st.info(f"📊 **Data Sources Summary**: {dict(source_stats)} | **Primary Source**: {max(source_stats, key=source_stats.get)}")
            
            if timeline:
                timeline_df = pd.DataFrame(timeline)
                
                # Filter out errors for signal analysis
                valid_timeline = timeline_df[timeline_df["Source"] != "Error"]
                
                if not valid_timeline.empty:
                    # Summary metrics
                    st.subheader(f"📊 Analysis Summary for {symbol}")
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    signal_counts = valid_timeline["Signal"].value_counts()
                    with col1:
                        st.metric("Strong Buy Signals", signal_counts.get("Strong Buy", 0))
                    with col2:
                        st.metric("Buy Signals", signal_counts.get("Buy", 0))
                    with col3:
                        st.metric("Neutral Signals", signal_counts.get("Neutral", 0))
                    with col4:
                        st.metric("Sell Signals", signal_counts.get("Sell", 0))
                    with col5:
                        st.metric("Strong Sell Signals", signal_counts.get("Strong Sell", 0))
                    
                    # Timeline display
                    st.subheader("📈 Trading Timeline")
                    
                    # Color coding function
                    def highlight_signals(row):
                        if row["Signal"] == "Strong Buy":
                            return ['background-color: #00ff00; color: black'] * len(row)
                        elif row["Signal"] == "Buy":
                            return ['background-color: #90ee90; color: black'] * len(row)
                        elif row["Signal"] == "Strong Sell":
                            return ['background-color: #ff0000; color: white'] * len(row)
                        elif row["Signal"] == "Sell":
                            return ['background-color: #ffcccb; color: black'] * len(row)
                        elif row["Signal"] == "Error":
                            return ['background-color: #ffcccc; color: red'] * len(row)
                        else:
                            return [''] * len(row)
                    
                    # Display timeline
                    display_columns = ["DateTime", "Day", "Signal", "Net_Score", "Bullish_Aspects", "Bearish_Aspects"]
                    if show_source_info:
                        display_columns.append("Source")
                    if show_transits:
                        display_columns.append("Transits")
                    if show_details:
                        display_columns.append("Signal_Details")
                    
                    display_df = timeline_df[display_columns]
                    styled_df = display_df.style.apply(highlight_signals, axis=1)
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # Interactive charts using valid data only
                    st.subheader("📊 Signal Strength Analysis")
                    
                    # Create subplots
                    fig = make_subplots(
                        rows=2, cols=1,
                        subplot_titles=('Bullish vs Bearish Scores', 'Net Score Trend'),
                        vertical_spacing=0.1
                    )
                    
                    # Bullish vs Bearish scores
                    fig.add_trace(
                        go.Scatter(x=valid_timeline["DateTime"], y=valid_timeline["Bullish_Score"],
                                  name="Bullish Score", line=dict(color="green", width=2)),
                        row=1, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=valid_timeline["DateTime"], y=valid_timeline["Bearish_Score"],
                                  name="Bearish Score", line=dict(color="red", width=2)),
                        row=1, col=1
                    )
                    
                    # Net score with color coding
                    colors = []
                    for _, row in valid_timeline.iterrows():
                        if row["Signal"] == "Strong Buy":
                            colors.append("darkgreen")
                        elif row["Signal"] == "Buy":
                            colors.append("lightgreen")
                        elif row["Signal"] == "Strong Sell":
                            colors.append("darkred")
                        elif row["Signal"] == "Sell":
                            colors.append("lightcoral")
                        else:
                            colors.append("gray")
                    
                    fig.add_trace(
                        go.Scatter(x=valid_timeline["DateTime"], y=valid_timeline["Net_Score"],
                                  name="Net Score", mode='lines+markers',
                                  line=dict(color="blue", width=2),
                                  marker=dict(color=colors, size=8)),
                        row=2, col=1
                    )
                    
                    # Add zero line for net score
                    fig.add_hline(y=0, line_dash="dash", line_color="black", row=2, col=1)
                    
                    fig.update_layout(
                        height=600,
                        title_text=f"Astrological Signal Analysis for {symbol} (Multi-Source Data)",
                        showlegend=True
                    )
                    
                    fig.update_xaxes(title_text="Time", row=2, col=1)
                    fig.update_yaxes(title_text="Score", row=1, col=1)
                    fig.update_yaxes(title_text="Net Score", row=2, col=1)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Key insights
                    st.subheader("🔍 Key Insights")
                    
                    if len(valid_timeline) > 0:
                        max_bullish = valid_timeline.loc[valid_timeline["Bullish_Score"].idxmax()]
                        max_bearish = valid_timeline.loc[valid_timeline["Bearish_Score"].idxmax()]
                        
                        insight_col1, insight_col2 = st.columns(2)
                        
                        with insight_col1:
                            st.info(f"""
                            **Strongest Bullish Signal:**
                            - Time: {max_bullish['DateTime']}
                            - Score: {max_bullish['Bullish_Score']:.2f}
                            - Signal: {max_bullish['Signal']}
                            - Source: {max_bullish['Source']}
                            """)
                        
                        with insight_col2:
                            st.warning(f"""
                            **Strongest Bearish Signal:**
                            - Time: {max_bearish['DateTime']}
                            - Score: {max_bearish['Bearish_Score']:.2f}
                            - Signal: {max_bearish['Signal']}
                            - Source: {max_bearish['Source']}
                            """)
                else:
                    st.error("❌ No valid data generated. Please check your settings and try again.")
            else:
                st.error("❌ No data generated. Please check your date/time range.")

# Enhanced instructions
st.markdown("""
### 📋 Multi-Source Data Integration

**🔄 Data Source Hierarchy:**
1. **🌐 Astronomics.ai API**: Real-time data (when available)
2. **🔭 Swiss Ephemeris**: Precise astronomical calculations (if installed)
3. **🎲 Simulation Mode**: Realistic approximations (always available)

**📊 Source Selection:**
- **Auto Mode**: Tries API → SwissEph → Simulation automatically
- **API Only**: Uses only astronomics.ai (shows errors if unavailable)
- **SwissEph Only**: Uses only Swiss Ephemeris calculations
- **Simulation Only**: Uses built-in simulation data

**🚀 Installation Options:**
```bash
# For Swiss Ephemeris support
pip install pyswisseph

# Basic requirements (simulation mode works without SwissEph)
pip install streamlit pandas numpy plotly requests
```

**🎯 Signal Interpretation:**
- 🟢 **Strong Buy**: >80% bullish dominance with strong beneficial aspects
- 🟢 **Buy**: 60-80% bullish tendency
- 🔴 **Strong Sell**: >80% bearish dominance with challenging aspects
- 🔴 **Sell**: 60-80% bearish tendency
- ⚪ **Neutral**: <60% dominance either way

This multi-source approach ensures **reliable astrological analysis** regardless of external API availability or library installation status.
""")
