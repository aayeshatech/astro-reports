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

# Nakshatra data with market characteristics
nakshatras = [
    ("Ashwini", 0, 13+20/60, "Impulsive", "High volatility, quick moves"),
    ("Bharani", 13+20/60, 26+40/60, "Restrictive", "Resistance levels, consolidation"),
    ("Krittika", 26+40/60, 40, "Sharp", "Sharp moves, breakouts"),
    ("Rohini", 40, 53+20/60, "Growth", "Steady uptrend, bull market"),
    ("Mrigashira", 53+20/60, 66+40/60, "Searching", "Range-bound, uncertainty"),
    ("Ardra", 66+40/60, 80, "Destructive", "High volatility, corrections"),
    ("Punarvasu", 80, 93+20/60, "Renewal", "Recovery, bounce back"),
    ("Pushya", 93+20/60, 106+40/60, "Nourishing", "Steady growth, accumulation"),
    ("Ashlesha", 106+40/60, 120, "Entangling", "Sideways, manipulation"),
    ("Magha", 120, 133+20/60, "Royal", "Leadership stocks outperform"),
    ("Purva Phalguni", 133+20/60, 146+40/60, "Enjoyment", "Consumption stocks up"),
    ("Uttara Phalguni", 146+40/60, 160, "Service", "Service sector strength"),
    ("Hasta", 160, 173+20/60, "Skillful", "Technical analysis works"),
    ("Chitra", 173+20/60, 186+40/60, "Beautiful", "Luxury goods, aesthetics"),
    ("Swati", 186+40/60, 200, "Independent", "Individual stock moves"),
    ("Vishakha", 200, 213+20/60, "Purposeful", "Directional moves"),
    ("Anuradha", 213+20/60, 226+40/60, "Friendly", "Broad market participation"),
    ("Jyeshtha", 226+40/60, 240, "Chief", "Large cap leadership"),
    ("Mula", 240, 253+20/60, "Root", "Fundamental analysis focus"),
    ("Purva Ashadha", 253+20/60, 266+40/60, "Invincible", "Strong trending moves"),
    ("Uttara Ashadha", 266+40/60, 280, "Victory", "Final push, completion"),
    ("Shravana", 280, 293+20/60, "Listening", "News-driven moves"),
    ("Dhanishta", 293+20/60, 306+40/60, "Wealthy", "Financial sector focus"),
    ("Shatabhisha", 306+40/60, 320, "Healing", "Recovery after correction"),
    ("Purva Bhadrapada", 320, 333+20/60, "Dual", "Mixed signals, confusion"),
    ("Uttara Bhadrapada", 333+20/60, 346+40/60, "Depth", "Value investing"),
    ("Revati", 346+40/60, 360, "Wealthy", "Prosperity, bull market end")
]

# Zodiac signs and market characteristics
zodiac_market_traits = {
    "Aries": {"trend": "Bullish", "volatility": "High", "sectors": "Energy, Defense"},
    "Taurus": {"trend": "Stable", "volatility": "Low", "sectors": "Banking, FMCG"},
    "Gemini": {"trend": "Volatile", "volatility": "Medium", "sectors": "IT, Communication"},
    "Cancer": {"trend": "Defensive", "volatility": "Medium", "sectors": "Healthcare, Food"},
    "Leo": {"trend": "Strong", "volatility": "Medium", "sectors": "Luxury, Entertainment"},
    "Virgo": {"trend": "Cautious", "volatility": "Low", "sectors": "Pharma, Services"},
    "Libra": {"trend": "Balanced", "volatility": "Low", "sectors": "Beauty, Fashion"},
    "Scorpio": {"trend": "Intense", "volatility": "High", "sectors": "Mining, Chemicals"},
    "Sagittarius": {"trend": "Optimistic", "volatility": "Medium", "sectors": "Travel, Education"},
    "Capricorn": {"trend": "Conservative", "volatility": "Low", "sectors": "Infrastructure, Realty"},
    "Aquarius": {"trend": "Innovative", "volatility": "High", "sectors": "Technology, Renewables"},
    "Pisces": {"trend": "Emotional", "volatility": "High", "sectors": "Water, Spiritual"}
}

# Market sessions
market_sessions = {
    "Pre-Market": {"start": "09:00", "end": "09:15", "characteristics": "Gap analysis"},
    "Opening": {"start": "09:15", "end": "10:00", "characteristics": "High volatility, trend setting"},
    "Morning": {"start": "10:00", "end": "11:30", "characteristics": "Primary trend development"},
    "Mid-Session": {"start": "11:30", "end": "13:30", "characteristics": "Institutional activity"},
    "Afternoon": {"start": "13:30", "end": "15:00", "characteristics": "Retail participation"},
    "Closing": {"start": "15:00", "end": "15:30", "characteristics": "Settlement, final moves"}
}

# Enhanced planet weights for aspect strength
planet_weights = {
    "Sun": 2.0, "Moon": 1.8, "Mars": 1.5, "Mercury": 1.2,
    "Jupiter": 2.2, "Venus": 1.6, "Saturn": 1.8,
    "Rahu": 1.4, "Ketu": 1.4
}

# Planetary market influences
planetary_influences = {
    "Sun": {"positive": "Leadership stocks, govt policies", "negative": "Ego-driven decisions"},
    "Moon": {"positive": "Sentiment, FMCG stocks", "negative": "Emotional trading"},
    "Mars": {"positive": "Energy, metals, defense", "negative": "Aggressive selling"},
    "Mercury": {"positive": "IT, communication, quick gains", "negative": "Volatility, confusion"},
    "Jupiter": {"positive": "Banking, finance, optimism", "negative": "Over-expansion"},
    "Venus": {"positive": "Luxury, beauty, consumption", "negative": "Speculation"},
    "Saturn": {"positive": "Infrastructure, discipline", "negative": "Restrictions, delays"},
    "Rahu": {"positive": "Innovation, foreign investment", "negative": "Illusion, manipulation"},
    "Ketu": {"positive": "Spiritual stocks, detachment", "negative": "Sudden exits"}
}

# Simulation data for when APIs are not available
def get_simulation_data(date_time):
    """Generate realistic planetary positions for simulation mode"""
    base_positions = {
        "Sun": {"longitude": 127.5, "sign": "Leo", "retrograde": False},
        "Moon": {"longitude": 165.3, "sign": "Virgo", "retrograde": False},
        "Mars": {"longitude": 52.1, "sign": "Taurus", "retrograde": False},
        "Mercury": {"longitude": 115.8, "sign": "Cancer", "retrograde": True},
        "Jupiter": {"longitude": 108.9, "sign": "Cancer", "retrograde": True},
        "Venus": {"longitude": 63.5, "sign": "Gemini", "retrograde": False},
        "Saturn": {"longitude": 340.2, "sign": "Pisces", "retrograde": True},
        "Rahu": {"longitude": 325.7, "sign": "Pisces", "retrograde": True},
        "Ketu": {"longitude": 145.7, "sign": "Virgo", "retrograde": True}
    }
    
    base_date = datetime(2025, 7, 30, 12, 0, 0)
    time_diff = (date_time - base_date).total_seconds() / 3600
    
    speeds = {
        "Sun": 0.041667, "Moon": 0.5416, "Mercury": 0.083, "Venus": 0.046,
        "Mars": 0.024, "Jupiter": 0.0033, "Saturn": 0.001389,
        "Rahu": -0.00217, "Ketu": -0.00217
    }
    
    updated_positions = {}
    for planet, data in base_positions.items():
        new_longitude = (data["longitude"] + speeds.get(planet, 0) * time_diff) % 360
        updated_positions[planet] = {
            "longitude": new_longitude,
            "retrograde": data["retrograde"]
        }
    
    return updated_positions

@st.cache_data(ttl=3600)
def fetch_astronomics_data(date_str, time_str=None):
    """Attempt to fetch astronomical data from astronomics.ai API"""
    try:
        base_url = "https://data.astronomics.ai/almanac/"
        url = f"{base_url}?date={date_str}&time={time_str}" if time_str else f"{base_url}?date={date_str}"
        
        headers = {
            'User-Agent': 'Astro-Market-Analyzer/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data, "API"
        else:
            return None, f"API_ERROR_{response.status_code}"
            
    except Exception:
        return None, "CONNECTION_ERROR"

def get_nakshatra_pada(degree):
    """Calculate Nakshatra and Pada from longitude"""
    for nak_data in nakshatras:
        nak, start, end = nak_data[0], nak_data[1], nak_data[2]
        if start <= degree < end:
            pada = int((degree - start) // (13+20/60 / 4)) + 1
            return nak, pada, nak_data[3], nak_data[4]  # Include characteristics
    return "Unknown", 0, "Neutral", "No specific influence"

def get_zodiac_house(degree):
    """Get zodiac sign and house from longitude"""
    sign_index = int(degree // 30) % 12
    house_index = int(degree // 30) % 12
    sign = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"][sign_index]
    house = f"House {house_index + 1}"
    return sign, house

def convert_degree_to_dms(degree):
    """Convert decimal degree to degrees, minutes, seconds format"""
    degree_in_sign = degree % 30
    degree_int = int(degree_in_sign)
    minute_int = int((degree_in_sign - degree_int) * 60)
    second_int = int(((degree_in_sign - degree_int) * 60 - minute_int) * 60)
    return f"{degree_int}° {minute_int}' {second_int}\""

def get_planetary_positions_swisseph(date_time):
    """Calculate planetary positions using Swiss Ephemeris"""
    if not SWISSEPH_AVAILABLE:
        return pd.DataFrame()
    
    try:
        utc_offset = 5.5
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
                nak, pada, nak_nature, nak_influence = get_nakshatra_pada(lon_sid)
                
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
                    "Source": "SwissEph",
                    "Nakshatra_Nature": nak_nature,
                    "Market_Influence": nak_influence
                })
                
            except Exception:
                continue
        
        return pd.DataFrame(positions)
        
    except Exception:
        return pd.DataFrame()

def get_planetary_positions_simulation(date_time):
    """Get planetary positions using simulation data"""
    try:
        sim_data = get_simulation_data(date_time)
        positions = []
        
        for planet, data in sim_data.items():
            longitude = data["longitude"]
            sign, house = get_zodiac_house(longitude)
            nak, pada, nak_nature, nak_influence = get_nakshatra_pada(longitude)
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
                "Source": "Simulation",
                "Nakshatra_Nature": nak_nature,
                "Market_Influence": nak_influence
            })
        
        return pd.DataFrame(positions)
        
    except Exception:
        return pd.DataFrame()

def get_planetary_positions(date_time, data_source="auto"):
    """Get planetary positions with fallback priority"""
    positions = pd.DataFrame()
    source_used = "None"
    
    if data_source in ["auto", "api"]:
        date_str = date_time.strftime("%Y-%m-%d")
        time_str = date_time.strftime("%H:%M:%S")
        api_data, api_status = fetch_astronomics_data(date_str, time_str)
        
        if api_data and api_status == "API":
            source_used = "API"
    
    if positions.empty and data_source in ["auto", "swisseph"] and SWISSEPH_AVAILABLE:
        positions = get_planetary_positions_swisseph(date_time)
        if not positions.empty:
            source_used = "SwissEph"
    
    if positions.empty:
        positions = get_planetary_positions_simulation(date_time)
        source_used = "Simulation"
    
    return positions, source_used

def get_aspects(positions):
    """Calculate aspects between planets with market context"""
    if positions.empty:
        return pd.DataFrame(), []
    
    aspects = []
    planets = positions["Planet"].tolist()
    full_degrees = positions["Full_Degree"].tolist()
    
    aspect_config = {
        0: ("Conjunction", 2.0, "Unity", "Combined planetary energy"),
        60: ("Sextile", 2.0, "Opportunity", "Favorable trading opportunities"),
        90: ("Square", 2.0, "Tension", "Market stress, volatility"),
        120: ("Trine", 2.0, "Harmony", "Smooth trending moves"),
        180: ("Opposition", 2.0, "Conflict", "Reversal potential"),
        30: ("Semisextile", 1.0, "Adjustment", "Minor corrections"),
        45: ("Semisquare", 1.0, "Friction", "Intraday volatility"),
        135: ("Sesquiquadrate", 1.0, "Crisis", "Sharp moves"),
        150: ("Quincunx", 1.0, "Adjustment", "Unexpected moves")
    }
    
    for i, p1 in enumerate(planets):
        for j, p2 in enumerate(planets[i+1:], start=i+1):
            deg1 = full_degrees[i]
            deg2 = full_degrees[j]
            diff = abs(deg2 - deg1)
            if diff > 180:
                diff = 360 - diff
            
            for angle, (aspect_name, orb, nature, market_effect) in aspect_config.items():
                if abs(diff - angle) <= orb:
                    weight = (planet_weights.get(p1, 1.0) + planet_weights.get(p2, 1.0)) / 2
                    
                    # Market-specific tendency
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
                        "Strength": "Strong" if abs(diff - angle) <= orb/2 else "Moderate",
                        "Nature": nature,
                        "Market_Effect": market_effect
                    })
                    break
    
    return pd.DataFrame(aspects), aspects

def analyze_market_session(time_str, aspects_df, positions_df):
    """Analyze market characteristics for specific session"""
    hour = int(time_str.split(':')[0])
    minute = int(time_str.split(':')[1])
    time_decimal = hour + minute/60
    
    # Determine session
    if 9.0 <= time_decimal < 9.25:
        session = "Pre-Market"
    elif 9.25 <= time_decimal < 10.0:
        session = "Opening"
    elif 10.0 <= time_decimal < 11.5:
        session = "Morning"
    elif 11.5 <= time_decimal < 13.5:
        session = "Mid-Session"
    elif 13.5 <= time_decimal < 15.0:
        session = "Afternoon"
    elif 15.0 <= time_decimal <= 15.5:
        session = "Closing"
    else:
        session = "After-Hours"
    
    # Calculate session characteristics
    bullish_count = len(aspects_df[aspects_df["Tendency"] == "Bullish"])
    bearish_count = len(aspects_df[aspects_df["Tendency"] == "Bearish"])
    
    # Determine session outlook
    if bullish_count > bearish_count * 1.5:
        outlook = "Strong Bullish"
        emoji = "🚀"
    elif bullish_count > bearish_count:
        outlook = "Bullish"
        emoji = "📈"
    elif bearish_count > bullish_count * 1.5:
        outlook = "Strong Bearish"
        emoji = "📉"
    elif bearish_count > bullish_count:
        outlook = "Bearish"
        emoji = "🔻"
    else:
        outlook = "Neutral"
        emoji = "➡️"
    
    return {
        "session": session,
        "outlook": outlook,
        "emoji": emoji,
        "bullish_aspects": bullish_count,
        "bearish_aspects": bearish_count
    }

def generate_market_insights(positions_df, aspects_df):
    """Generate detailed market insights like DeepSeek report"""
    insights = []
    
    # Key planetary influences
    key_influences = []
    for _, pos in positions_df.iterrows():
        planet = pos["Planet"]
        sign = pos["Sign"]
        retro = pos["Retrograde"]
        
        trait = zodiac_market_traits.get(sign, {})
        
        if planet in ["Sun", "Moon", "Mercury", "Jupiter"]:
            retro_text = " (Retrograde)" if retro == "Yes" else ""
            influence_text = f"{planet} in {sign}{retro_text} → {trait.get('trend', 'Neutral')} sentiment"
            
            if planet == "Mercury" and retro == "Yes":
                influence_text += " → Volatility in banking/financials"
            elif planet == "Moon":
                influence_text += f" → {trait.get('sectors', 'General')} focus"
            
            key_influences.append(influence_text)
    
    # Critical aspects
    critical_aspects = []
    for _, aspect in aspects_df.iterrows():
        if aspect["Strength"] == "Strong":
            effect = "Recovery" if aspect["Tendency"] == "Bullish" else "Pressure"
            critical_aspects.append(f"{aspect['Planet1']}-{aspect['Planet2']} {aspect['Aspect']} → {effect}")
    
    return {
        "key_influences": key_influences,
        "critical_aspects": critical_aspects
    }

def generate_daily_report(date, positions_df, timeline_df):
    """Generate comprehensive daily report like DeepSeek"""
    date_str = date.strftime("%d-%b-%Y").upper()
    
    # Header
    report = f"""
## 📈📉 NIFTY & BANKNIFTY ASTRO TREND REPORT | {date_str}
**Market Hours: 9:15 AM - 3:30 PM IST**

### 🌕 KEY PLANETARY INFLUENCES
"""
    
    # Add planetary influences
    for _, pos in positions_df.iterrows():
        if pos["Planet"] in ["Sun", "Moon", "Mercury", "Jupiter", "Mars"]:
            sign = pos["Sign"]
            retro = " (Retrograde)" if pos["Retrograde"] == "Yes" else ""
            trait = zodiac_market_traits.get(sign, {})
            
            report += f"- **{pos['Planet']} in {sign}{retro}** → {trait.get('trend', 'Neutral')} sentiment, {trait.get('sectors', 'General')} focus\n"
    
    # Session analysis
    report += "\n### ⏰ INTRADAY TREND TIMELINE\n"
    
    # Group timeline by sessions
    sessions = {
        "🌅 Morning (9:15-11:30 AM)": [],
        "🌇 Mid-Session (11:30 AM-1:30 PM)": [],
        "🌆 Afternoon (1:30-3:30 PM)": []
    }
    
    for _, row in timeline_df.iterrows():
        time_str = row["DateTime"].split(" ")[1]
        hour = int(time_str.split(":")[0])
        
        if 9 <= hour < 11.5:
            session_key = "🌅 Morning (9:15-11:30 AM)"
        elif 11.5 <= hour < 13.5:
            session_key = "🌇 Mid-Session (11:30 AM-1:30 PM)"
        else:
            session_key = "🌆 Afternoon (1:30-3:30 PM)"
        
        signal_emoji = "📈" if "Buy" in row["Signal"] else "📉" if "Sell" in row["Signal"] else "➡️"
        sessions[session_key].append(f"{time_str} → {signal_emoji} {row['Signal']}")
    
    for session_name, signals in sessions.items():
        if signals:
            report += f"\n**{session_name}**\n"
            for signal in signals[:3]:  # Show first 3 signals per session
                report += f"- {signal}\n"
    
    # Overall outlook
    bullish_signals = len(timeline_df[timeline_df["Signal"].str.contains("Buy", na=False)])
    bearish_signals = len(timeline_df[timeline_df["Signal"].str.contains("Sell", na=False)])
    
    if bullish_signals > bearish_signals:
        overall_outlook = "🟢 Bullish (Opportunity for gains)"
    elif bearish_signals > bullish_signals:
        overall_outlook = "🔴 Bearish (Caution advised)"
    else:
        overall_outlook = "🟡 Neutral (Range-bound trading)"
    
    # Critical times (highest activity)
    critical_times = timeline_df.nlargest(2, "Active_Aspects")["DateTime"].str.split(" ").str[1].tolist()
    
    report += f"""
### 🎯 FINAL OUTLOOK
- **Overall**: {overall_outlook}
- **Critical Times**: {", ".join(critical_times)}
- **Key Strategy**: {"Buy on dips" if bullish_signals > bearish_signals else "Sell on rallies" if bearish_signals > bullish_signals else "Range trading"}
"""
    
    return report

# Streamlit app
st.set_page_config(layout="wide", page_title="Enhanced Astro Market Analyzer - DeepSeek Style")
st.title("🌟 Enhanced Astro Market Analyzer")
st.subheader("🔮 Advanced Planetary Transit Analysis for Market Timing")

# Custom CSS
st.markdown("""
    <style>
    .stDataFrame { width: 100%; }
    .metric-container { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; }
    .signal-strong-buy { background-color: #00ff00; color: black; }
    .signal-buy { background-color: #90ee90; color: black; }
    .signal-sell { background-color: #ffcccb; color: black; }
    .signal-strong-sell { background-color: #ff0000; color: white; }
    .signal-neutral { background-color: #d3d3d3; color: black; }
    .daily-report { background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #007bff; }
    </style>
""", unsafe_allow_html=True)

# Data Source Selection
st.sidebar.header("📊 Data Source Settings")
with st.sidebar:
    data_source = st.selectbox(
        "Primary Data Source",
        ["auto", "swisseph", "simulation"],
        format_func=lambda x: {
            "auto": "🔄 Auto (SwissEph → Simulation)",
            "swisseph": "🔭 Swiss Ephemeris Only",
            "simulation": "🎲 Simulation Mode Only"
        }[x]
    )
    
    # Display status
    if SWISSEPH_AVAILABLE:
        st.success("✅ Swiss Ephemeris Available")
    else:
        st.warning("⚠️ Swiss Ephemeris Not Installed - Using Simulation")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Current Analysis", "🔍 Intraday Analysis", "📋 Daily Report"])

# Current Analysis Tab
with tab1:
    st.header("Current Planetary Positions & Market Impact")
    
    current_time = datetime.now()
    with st.spinner("Fetching current planetary data..."):
        current_positions, source_used = get_planetary_positions(current_time, data_source)
        
        if not current_positions.empty:
            st.success(f"🔭 Data Source: **{source_used}** | Time: {current_time.strftime('%Y-%m-%d %H:%M')} IST")
            
            # Enhanced positions display
            display_positions = current_positions[["Planet", "Sign", "Degree", "Nakshatra", "Retrograde", "Nakshatra_Nature", "Market_Influence"]]
            st.dataframe(display_positions, use_container_width=True)
            
            # Current aspects with market context
            current_aspects_df, _ = get_aspects(current_positions)
            if not current_aspects_df.empty:
                st.subheader("Active Aspects & Market Effects")
                aspect_display = current_aspects_df[["Planet1", "Planet2", "Aspect", "Tendency", "Strength", "Weight", "Market_Effect"]]
                st.dataframe(aspect_display, use_container_width=True)
                
                # Market session analysis
                current_session = analyze_market_session(current_time.strftime("%H:%M"), current_aspects_df, current_positions)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Current Session", f"{current_session['emoji']} {current_session['session']}")
                with col2:
                    st.metric("Session Outlook", current_session["outlook"])
                with col3:
                    st.metric("Bullish Aspects", current_session["bullish_aspects"])
                with col4:
                    st.metric("Bearish Aspects", current_session["bearish_aspects"])
                
                # Market insights
                insights = generate_market_insights(current_positions, current_aspects_df)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🌟 Key Planetary Influences")
                    for influence in insights["key_influences"]:
                        st.write(f"• {influence}")
                
                with col2:
                    st.subheader("⚡ Critical Aspects")
                    for aspect in insights["critical_aspects"]:
                        st.write(f"• {aspect}")

# Intraday Analysis Tab
with tab2:
    st.header("🚀 Enhanced Intraday Analysis")
    
    with st.container():
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📈 Analysis Settings")
            symbol = st.text_input("Stock Symbol", "NIFTY", help="Enter NIFTY or BANKNIFTY")
            analysis_date = st.date_input("Analysis Date", datetime(2025, 7, 30))
            
        with col2:
            st.subheader("⚙️ Time Settings")
            start_time = st.time_input("Start Time (IST)", datetime(2025, 7, 30, 9, 15).time())
            end_time = st.time_input("End Time (IST)", datetime(2025, 7, 30, 15, 30).time())
            time_interval = st.selectbox("Interval", ["15 minutes", "30 minutes"], index=0)
    
    if st.button("🔮 Generate Intraday Analysis", type="primary"):
        start_datetime = datetime.combine(analysis_date, start_time)
        end_datetime = datetime.combine(analysis_date, end_time)
        
        if start_datetime >= end_datetime:
            st.error("❌ End time must be after start time.")
        else:
            interval_minutes = 15 if time_interval == "15 minutes" else 30
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            timeline = []
            previous_positions = None
            previous_aspects_df = pd.DataFrame()
            
            total_intervals = int((end_datetime - start_datetime).total_seconds() / (interval_minutes * 60))
            current_time = start_datetime
            interval_count = 0
            
            while current_time <= end_datetime:
                progress = min(interval_count / max(total_intervals, 1), 1.0)
                progress_bar.progress(progress)
                status_text.text(f"Analyzing: {current_time.strftime('%H:%M')} ({interval_count + 1}/{total_intervals + 1})")
                
                positions, source_used = get_planetary_positions(current_time, data_source)
                
                if not positions.empty:
                    current_aspects_df, aspects_list = get_aspects(positions)
                    
                    # Session analysis
                    session_analysis = analyze_market_session(current_time.strftime("%H:%M"), current_aspects_df, positions)
                    
                    # Detect transits
                    transits = []
                    if previous_positions is not None:
                        for _, current_row in positions.iterrows():
                            planet = current_row["Planet"]
                            prev_row = previous_positions[previous_positions["Planet"] == planet]
                            
                            if not prev_row.empty:
                                prev_row = prev_row.iloc[0]
                                if current_row["Sign"] != prev_row["Sign"]:
                                    transits.append(f"{planet}: {prev_row['Sign']} → {current_row['Sign']}")
                                elif current_row["Nakshatra"] != prev_row["Nakshatra"]:
                                    transits.append(f"{planet}: {prev_row['Nakshatra']} → {current_row['Nakshatra']}")
                    
                    # Calculate scores
                    bullish_score = sum([row["Weight"] for _, row in current_aspects_df.iterrows() if row["Tendency"] == "Bullish"])
                    bearish_score = sum([row["Weight"] for _, row in current_aspects_df.iterrows() if row["Tendency"] == "Bearish"])
                    net_score = bullish_score - bearish_score
                    
                    # Determine signal
                    if net_score > 3:
                        signal = "Strong Buy"
                    elif net_score > 1:
                        signal = "Buy"
                    elif net_score < -3:
                        signal = "Strong Sell"
                    elif net_score < -1:
                        signal = "Sell"
                    else:
                        signal = "Neutral"
                    
                    timeline.append({
                        "DateTime": current_time.strftime("%Y-%m-%d %H:%M"),
                        "Day": current_time.strftime("%A"),
                        "Session": session_analysis["session"],
                        "Signal": signal,
                        "Net_Score": net_score,
                        "Bullish_Aspects": session_analysis["bullish_aspects"],
                        "Bearish_Aspects": session_analysis["bearish_aspects"],
                        "Transits": "; ".join(transits) if transits else "None",
                        "Session_Outlook": session_analysis["outlook"],
                        "Source": source_used,
                        "Active_Aspects": len(current_aspects_df)
                    })
                    
                    previous_positions = positions.copy()
                    previous_aspects_df = current_aspects_df.copy()
                
                current_time += timedelta(minutes=interval_minutes)
                interval_count += 1
            
            progress_bar.progress(1.0)
            status_text.text("✅ Analysis Complete!")
            
            if timeline:
                timeline_df = pd.DataFrame(timeline)
                
                # Summary metrics
                st.subheader(f"📊 {symbol} Intraday Summary - {analysis_date.strftime('%d %b %Y')}")
                
                signal_counts = timeline_df["Signal"].value_counts()
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Strong Buy", signal_counts.get("Strong Buy", 0))
                with col2:
                    st.metric("Buy", signal_counts.get("Buy", 0))
                with col3:
                    st.metric("Neutral", signal_counts.get("Neutral", 0))
                with col4:
                    st.metric("Sell", signal_counts.get("Sell", 0))
                with col5:
                    st.metric("Strong Sell", signal_counts.get("Strong Sell", 0))
                
                # Timeline display
                st.subheader("📈 Detailed Timeline")
                
                def highlight_signals(row):
                    if row["Signal"] == "Strong Buy":
                        return ['background-color: #00ff00; color: black'] * len(row)
                    elif row["Signal"] == "Buy":
                        return ['background-color: #90ee90; color: black'] * len(row)
                    elif row["Signal"] == "Strong Sell":
                        return ['background-color: #ff0000; color: white'] * len(row)
                    elif row["Signal"] == "Sell":
                        return ['background-color: #ffcccb; color: black'] * len(row)
                    else:
                        return [''] * len(row)
                
                display_columns = ["DateTime", "Session", "Signal", "Net_Score", "Session_Outlook", "Transits"]
                display_df = timeline_df[display_columns]
                styled_df = display_df.style.apply(highlight_signals, axis=1)
                st.dataframe(styled_df, use_container_width=True)
                
                # Charts
                st.subheader("📊 Signal Strength Visualization")
                
                fig = make_subplots(rows=2, cols=1, subplot_titles=('Session Analysis', 'Net Score Trend'))
                
                # Session outlook
                session_colors = {"Strong Bullish": "darkgreen", "Bullish": "green", "Neutral": "gray", 
                                "Bearish": "red", "Strong Bearish": "darkred"}
                colors = [session_colors.get(outlook, "gray") for outlook in timeline_df["Session_Outlook"]]
                
                fig.add_trace(
                    go.Scatter(x=timeline_df["DateTime"], y=timeline_df["Bullish_Aspects"],
                              name="Bullish Aspects", line=dict(color="green")), row=1, col=1)
                fig.add_trace(
                    go.Scatter(x=timeline_df["DateTime"], y=timeline_df["Bearish_Aspects"],
                              name="Bearish Aspects", line=dict(color="red")), row=1, col=1)
                
                fig.add_trace(
                    go.Scatter(x=timeline_df["DateTime"], y=timeline_df["Net_Score"],
                              name="Net Score", mode='lines+markers', 
                              line=dict(color="blue"), marker=dict(color=colors, size=8)), row=2, col=1)
                
                fig.add_hline(y=0, line_dash="dash", line_color="black", row=2, col=1)
                
                fig.update_layout(height=600, title_text=f"{symbol} Intraday Astro Analysis")
                st.plotly_chart(fig, use_container_width=True)

# Daily Report Tab
with tab3:
    st.header("📋 Comprehensive Daily Report")
    
    report_date = st.date_input("Select Report Date", datetime(2025, 7, 30))
    
    if st.button("📊 Generate Daily Report", type="primary"):
        with st.spinner("Generating comprehensive daily report..."):
            # Generate full day analysis
            start_time = datetime.combine(report_date, datetime.strptime("09:15", "%H:%M").time())
            end_time = datetime.combine(report_date, datetime.strptime("15:30", "%H:%M").time())
            
            timeline = []
            current_time = start_time
            
            while current_time <= end_time:
                positions, source_used = get_planetary_positions(current_time, data_source)
                
                if not positions.empty:
                    aspects_df, _ = get_aspects(positions)
                    session_analysis = analyze_market_session(current_time.strftime("%H:%M"), aspects_df, positions)
                    
                    bullish_score = sum([row["Weight"] for _, row in aspects_df.iterrows() if row["Tendency"] == "Bullish"])
                    bearish_score = sum([row["Weight"] for _, row in aspects_df.iterrows() if row["Tendency"] == "Bearish"])
                    net_score = bullish_score - bearish_score
                    
                    if net_score > 3:
                        signal = "Strong Buy"
                    elif net_score > 1:
                        signal = "Buy"
                    elif net_score < -3:
                        signal = "Strong Sell"
                    elif net_score < -1:
                        signal = "Sell"
                    else:
                        signal = "Neutral"
                    
                    timeline.append({
                        "DateTime": current_time.strftime("%Y-%m-%d %H:%M"),
                        "Signal": signal,
                        "Active_Aspects": len(aspects_df)
                    })
                
                current_time += timedelta(minutes=30)
            
            # Generate positions for the day
            day_positions, _ = get_planetary_positions(start_time, data_source)
            timeline_df = pd.DataFrame(timeline)
            
            # Generate and display the report
            daily_report = generate_daily_report(report_date, day_positions, timeline_df)
            
            st.markdown('<div class="daily-report">', unsafe_allow_html=True)
            st.markdown(daily_report)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Additional analysis
            st.subheader("📊 Statistical Summary")
            
            if not timeline_df.empty:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    buy_signals = len(timeline_df[timeline_df["Signal"].str.contains("Buy", na=False)])
                    st.metric("Total Buy Signals", buy_signals)
                
                with col2:
                    sell_signals = len(timeline_df[timeline_df["Signal"].str.contains("Sell", na=False)])
                    st.metric("Total Sell Signals", sell_signals)
                
                with col3:
                    max_activity = timeline_df["Active_Aspects"].max()
                    st.metric("Peak Activity (Aspects)", max_activity)

# Instructions
st.markdown("""
### 📋 DeepSeek-Style Astro Analysis Features

**🔮 Enhanced Capabilities:**
- **Market Session Analysis**: Opening, morning, mid-session, afternoon timing
- **Planetary Influence Context**: Direct market impact interpretation
- **Critical Time Identification**: Peak activity periods
- **Comprehensive Daily Reports**: DeepSeek-style professional format
- **Nakshatra Market Characteristics**: Specific trading influences

**📊 Advanced Features:**
- **Session-wise Outlook**: Bullish/Bearish predictions per time period
- **Market Effect Descriptions**: Specific aspect impacts on trading
- **Professional Report Generation**: Daily comprehensive analysis
- **Critical Timing**: Identification of key reversal/momentum periods

**🎯 Usage for Daily Trading:**
1. Check **Current Analysis** for real-time market sentiment
2. Use **Intraday Analysis** for session-wise trading strategy
3. Generate **Daily Report** for comprehensive market outlook

This enhanced system now provides **professional-grade astrological market analysis** similar to DeepSeek's format with detailed timing predictions and market-specific interpretations.
""")
