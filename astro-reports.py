import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import json
import time

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

# Cache for API responses to avoid repeated calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_astronomics_data(date_str, time_str=None):
    """
    Fetch astronomical data from astronomics.ai API
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
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            st.warning(f"API returned status code: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("API request timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to astronomics.ai API. Please check your internet connection.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("Invalid JSON response from API")
        return None
    except Exception as e:
        st.error(f"Unexpected error fetching data: {str(e)}")
        return None

def parse_astronomics_response(api_data):
    """
    Parse the response from astronomics.ai API and extract planetary positions
    """
    if not api_data:
        return None
    
    try:
        positions = {}
        aspects = []
        
        # Different possible response structures from the API
        if 'planets' in api_data:
            planets_data = api_data['planets']
        elif 'positions' in api_data:
            planets_data = api_data['positions']
        elif 'ephemeris' in api_data:
            planets_data = api_data['ephemeris']
        else:
            # If the API returns planetary data directly
            planets_data = api_data
        
        # Map common planet name variations
        planet_mappings = {
            'sun': 'Sun', 'moon': 'Moon', 'mars': 'Mars', 'mercury': 'Mercury',
            'jupiter': 'Jupiter', 'venus': 'Venus', 'saturn': 'Saturn',
            'rahu': 'Rahu', 'ketu': 'Ketu', 'north_node': 'Rahu', 'south_node': 'Ketu',
            'northnode': 'Rahu', 'southnode': 'Ketu', 'mean_node': 'Rahu'
        }
        
        for planet_key, planet_data in planets_data.items():
            if isinstance(planet_data, dict):
                # Normalize planet name
                planet_name = planet_mappings.get(planet_key.lower(), planet_key.capitalize())
                
                # Extract position data
                position_info = {}
                
                # Try different possible field names for longitude
                longitude = None
                for lng_field in ['longitude', 'lng', 'lon', 'degree', 'position', 'ecliptic_longitude']:
                    if lng_field in planet_data:
                        longitude = float(planet_data[lng_field])
                        break
                
                if longitude is not None:
                    position_info['longitude'] = longitude
                    
                    # Try to get sign information
                    if 'sign' in planet_data:
                        position_info['sign'] = planet_data['sign']
                    
                    # Try to get nakshatra information
                    if 'nakshatra' in planet_data:
                        position_info['nakshatra'] = planet_data['nakshatra']
                    
                    # Try to get retrograde information
                    retrograde = False
                    for retro_field in ['retrograde', 'retro', 'is_retrograde']:
                        if retro_field in planet_data:
                            retrograde = bool(planet_data[retro_field])
                            break
                    position_info['retrograde'] = retrograde
                    
                    positions[planet_name] = position_info
        
        # Try to extract aspects if available
        if 'aspects' in api_data:
            aspects = api_data['aspects']
        elif 'planetary_aspects' in api_data:
            aspects = api_data['planetary_aspects']
        
        return {
            'positions': positions,
            'aspects': aspects,
            'timestamp': api_data.get('timestamp', ''),
            'date': api_data.get('date', ''),
            'time': api_data.get('time', '')
        }
        
    except Exception as e:
        st.error(f"Error parsing API response: {str(e)}")
        return None

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

def get_planetary_positions_from_api(date_time):
    """
    Get planetary positions using astronomics.ai API
    """
    try:
        # Format date and time for API
        date_str = date_time.strftime("%Y-%m-%d")
        time_str = date_time.strftime("%H:%M:%S")
        
        # Fetch data from API
        api_data = fetch_astronomics_data(date_str, time_str)
        
        if not api_data:
            st.warning(f"No data received from API for {date_str} {time_str}")
            return pd.DataFrame()
        
        # Parse the API response
        parsed_data = parse_astronomics_response(api_data)
        
        if not parsed_data or not parsed_data['positions']:
            st.warning("No planetary position data found in API response")
            return pd.DataFrame()
        
        positions = []
        
        # Process each planet
        for planet, pos_data in parsed_data['positions'].items():
            try:
                longitude = pos_data['longitude']
                
                # Get sign and house
                if 'sign' in pos_data:
                    sign = pos_data['sign']
                else:
                    sign, _ = get_zodiac_house(longitude)
                
                # Get nakshatra and pada
                if 'nakshatra' in pos_data:
                    nakshatra = pos_data['nakshatra']
                    pada = 1  # Default if not provided
                else:
                    nakshatra, pada = get_nakshatra_pada(longitude)
                
                # Get retrograde status
                is_retro = "Yes" if pos_data.get('retrograde', False) else "No"
                
                # Format degree
                degree_formatted = convert_degree_to_dms(longitude)
                
                positions.append({
                    "Planet": planet,
                    "Sign": sign,
                    "Degree": degree_formatted,
                    "Full_Degree": longitude,
                    "House": get_zodiac_house(longitude)[1],
                    "Nakshatra": nakshatra,
                    "Pada": pada,
                    "Retrograde": is_retro,
                    "Date": date_time.strftime("%Y-%m-%d %H:%M:%S IST")
                })
                
            except Exception as e:
                st.warning(f"Error processing {planet}: {str(e)}")
                continue
        
        return pd.DataFrame(positions)
        
    except Exception as e:
        st.error(f"Error in get_planetary_positions_from_api: {str(e)}")
        return pd.DataFrame()

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
st.set_page_config(layout="wide", page_title="Enhanced Astro Market Analyzer - Astronomics.ai")
st.title("🌟 Enhanced Astro Market Analyzer")
st.subheader("🔗 Powered by Astronomics.ai API")

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
    .api-status {
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    .api-success { background-color: #d4edda; color: #155724; }
    .api-error { background-color: #f8d7da; color: #721c24; }
    </style>
""", unsafe_allow_html=True)

# API Status Check
st.sidebar.header("🔌 API Status")
with st.sidebar:
    if st.button("Test API Connection", type="primary"):
        with st.spinner("Testing API connection..."):
            test_data = fetch_astronomics_data("2025-07-30")
            if test_data:
                st.success("✅ API Connected Successfully")
                st.json({"sample_keys": list(test_data.keys())[:5]})
            else:
                st.error("❌ API Connection Failed")

# Tabs
tab1, tab2 = st.tabs(["📊 Planetary Report", "🔍 Enhanced Stock Analysis"])

# Planetary Report Tab
with tab1:
    st.header("Current Planetary Positions from Astronomics.ai")
    
    # Display current planetary positions
    current_time = datetime.now()
    with st.spinner("Fetching current planetary data..."):
        current_positions = get_planetary_positions_from_api(current_time)
        
        if not current_positions.empty:
            st.success(f"✅ Data fetched successfully for {current_time.strftime('%Y-%m-%d %H:%M')} IST")
            
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
            st.error("❌ Failed to fetch current planetary data")

# Enhanced Stock Search Tab
with tab2:
    st.header("🚀 Enhanced Stock Analysis with Astronomics.ai")
    
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
            show_api_calls = st.checkbox("Show API Call Details", False)
            
            interval_map = {"15 minutes": 15, "30 minutes": 30, "1 hour": 60, "2 hours": 120}
            interval_minutes = interval_map[time_interval]
    
    if st.button("🔮 Analyze Stock with Astronomics.ai", type="primary"):
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        
        if start_datetime >= end_datetime:
            st.error("❌ End datetime must be after start datetime.")
        else:
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            api_calls_text = st.empty()
            
            # Calculate timeline
            timeline = []
            previous_positions = None
            previous_aspects_df = pd.DataFrame()
            api_call_count = 0
            failed_calls = 0
            
            total_intervals = int((end_datetime - start_datetime).total_seconds() / (interval_minutes * 60))
            current_time = start_datetime
            interval_count = 0
            
            while current_time <= end_datetime:
                # Update progress
                progress = min(interval_count / max(total_intervals, 1), 1.0)
                progress_bar.progress(progress)
                status_text.text(f"Analyzing: {current_time.strftime('%Y-%m-%d %H:%M')} ({interval_count + 1}/{total_intervals + 1})")
                
                if show_api_calls:
                    api_calls_text.text(f"API Calls: {api_call_count} | Failed: {failed_calls}")
                
                # Get current positions from API
                positions = get_planetary_positions_from_api(current_time)
                api_call_count += 1
                
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
                        "Transits": "; ".join(transits) if transits else "None",
                        "Active_Aspects": len(current_aspects_df),
                        "Bullish_Aspects": aspect_counts.get("Bullish", 0),
                        "Bearish_Aspects": aspect_counts.get("Bearish", 0),
                        "Signal": signal,
                        "Bullish_Score": bull_score,
                        "Bearish_Score": bear_score,
                        "Net_Score": bull_score - bear_score,
                        "Signal_Details": signal_details if show_details else "",
                        "Color": color,
                        "API_Success": True
                    })
                    
                    previous_positions = positions.copy()
                    previous_aspects_df = current_aspects_df.copy()
                else:
                    failed_calls += 1
                    # Add neutral entry for failed API calls
                    timeline.append({
                        "DateTime": current_time.strftime("%Y-%m-%d %H:%M"),
                        "Day": current_time.strftime("%A"),
                        "Transits": "API Error",
                        "Active_Aspects": 0,
                        "Bullish_Aspects": 0,
                        "Bearish_Aspects": 0,
                        "Signal": "API Error",
                        "Bullish_Score": 0,
                        "Bearish_Score": 0,
                        "Net_Score": 0,
                        "Signal_Details": "Failed to fetch data",
                        "Color": "red",
                        "API_Success": False
                    })
                
                current_time += timedelta(minutes=interval_minutes)
                interval_count += 1
                
                # Add small delay to avoid overwhelming the API
                time.sleep(0.5)
            
            progress_bar.progress(1.0)
            status_text.text("✅ Analysis Complete!")
            
            # API Summary
            success_rate = ((api_call_count - failed_calls) / api_call_count * 100) if api_call_count > 0 else 0
            st.info(f"📊 API Summary: {api_call_count} total calls, {failed_calls} failed, {success_rate:.1f}% success rate")
            
            if timeline:
                timeline_df = pd.DataFrame(timeline)
                
                # Filter out API errors for signal analysis
                valid_timeline = timeline_df[timeline_df["API_Success"] == True]
                
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
                        elif row["Signal"] == "API Error":
                            return ['background-color: #ffcccc; color: red'] * len(row)
                        else:
                            return [''] * len(row)
                    
                    # Display timeline
                    display_columns = ["DateTime", "Day", "Signal", "Net_Score", "Bullish_Aspects", "Bearish_Aspects"]
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
                        title_text=f"Astrological Signal Analysis for {symbol} (Astronomics.ai Data)",
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
                            """)
                        
                        with insight_col2:
                            st.warning(f"""
                            **Strongest Bearish Signal:**
                            - Time: {max_bearish['DateTime']}
                            - Score: {max_bearish['Bearish_Score']:.2f}
                            - Signal: {max_bearish['Signal']}
                            """)
                else:
                    st.error("❌ No valid data retrieved from API. Please check the API status and try again.")
            else:
                st.error("❌ No data generated. Please check your date/time range and API connectivity.")

# Enhanced instructions
st.markdown("""
### 📋 Enhanced Instructions - Astronomics.ai Integration

**🔗 API Integration Features:**
- ⚡ **Real-time Data**: Fetches live planetary positions from astronomics.ai
- 🔄 **Smart Caching**: 1-hour cache to optimize API usage
- 🛡️ **Error Handling**: Robust error handling with detailed status reporting
- 📊 **API Monitoring**: Track success rates and failed calls

**🚀 Usage:**
1. **Test API Connection**: Use sidebar button to verify astronomics.ai connectivity
2. **Stock Analysis**: 
   - Enter stock symbol and time range
   - Choose analysis interval (15min recommended for API efficiency)
   - Monitor API call success rate in real-time
3. **Signal Interpretation**:
   - 🟢 **Strong Buy**: >80% bullish dominance with strong beneficial aspects
   - 🟢 **Buy**: 60-80% bullish tendency
   - 🔴 **Strong Sell**: >80% bearish dominance with challenging aspects
   - 🔴 **Sell**: 60-80% bearish tendency
   - ⚪ **Neutral**: <60% dominance either way
   - 🔴 **API Error**: Failed to fetch data from astronomics.ai

**📝 Technical Notes:**
- API calls are made every analysis interval (15min/30min/1hr/2hr)
- Small delay between calls to respect API rate limits
- Automatic retry logic for failed requests
- Data validation and error reporting for API responses

**🔧 API Response Handling:**
- Supports multiple response formats from astronomics.ai
- Automatic planet name normalization
- Retrograde status detection
- Longitude to sign/nakshatra conversion
- Aspect calculation from positional data

This enhanced version provides reliable, real-time astrological data for accurate market timing analysis.
""")
