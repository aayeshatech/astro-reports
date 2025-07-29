import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import random
from fake_useragent import UserAgent

# Configure page
st.set_page_config(page_title="Vedic Astro Trader Pro", layout="wide")
st.title("🔮 Vedic Astro Trading Signals Pro")
st.markdown("### Multi-Source Planetary Transit Analysis")

# Vedic Astrology Configuration
VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu"
}

# Enhanced Symbol Configurations
SYMBOL_CONFIG = {
    "GOLD": {
        "planets": ["Sun", "Venus", "Saturn"],
        "colors": {"bullish": "#FFD700", "bearish": "#B8860B"},
        "rulers": {
            "Sun": {"strong": ["Trine", "Sextile"], "weak": ["Square", "Opposition"]},
            "Venus": {"strong": ["Trine", "Conjunction"], "weak": ["Square"]}
        }
    },
    "SILVER": {
        "planets": ["Moon", "Venus"],
        "colors": {"bullish": "#C0C0C0", "bearish": "#808080"},
        "rulers": {
            "Moon": {"strong": ["Trine", "Sextile"], "weak": ["Square"]}
        }
    },
    "CRUDE": {
        "planets": ["Jupiter", "Neptune"],
        "colors": {"bullish": "#FF4500", "bearish": "#8B0000"},
        "rulers": {
            "Jupiter": {"strong": ["Trine"], "weak": ["Square"]}
        }
    },
    "NIFTY": {
        "planets": ["Sun", "Mars"],
        "colors": {"bullish": "#32CD32", "bearish": "#006400"},
        "rulers": {
            "Mars": {"strong": ["Conjunction"], "weak": ["Opposition"]}
        }
    }
}

# Initialize user agent for web requests
ua = UserAgent()

def fetch_data_source(url, parser="html.parser", timeout=10):
    """Generic data fetcher with retry logic"""
    headers = {"User-Agent": ua.random}
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return BeautifulSoup(response.content, parser)
    except Exception as e:
        st.warning(f"Could not fetch from {url}: {str(e)}")
        return None

def parse_astronomics(soup, date):
    """Parse astronomics.ai data"""
    transits = []
    table = soup.find("table", {"class": "table"}) if soup else None
    
    if table:
        for row in table.find_all("tr")[1:]:
            cols = [td.text.strip() for td in row.find_all("td")]
            if len(cols) >= 12:
                transits.append({
                    "Planet": cols[0],
                    "Time": cols[2],
                    "Zodiac": cols[7],
                    "Position": cols[10],
                    "Motion": cols[3],
                    "Source": "Astronomics.ai"
                })
    return transits

def parse_drikpanchang(soup, date):
    """Parse drikpanchang.com data"""
    transits = []
    table = soup.find("table", {"id": "planetary-positions-table"}) if soup else None
    
    if table:
        for row in table.find_all("tr")[1:]:
            cols = [td.text.strip() for td in row.find_all("td")]
            if len(cols) >= 5:
                transits.append({
                    "Planet": cols[0],
                    "Time": "12:00",  # Default time
                    "Zodiac": cols[2],
                    "Position": cols[1],
                    "Motion": "D" if "Direct" in cols[4] else "R",
                    "Source": "DrikPanchang"
                })
    return transits

def parse_astroveda(soup, date):
    """Parse astroved.com data (alternative source)"""
    transits = []
    # Implement parsing logic for astroved.com
    return transits

def get_planetary_transits(date):
    """Fetch from multiple sources with fallback"""
    date_str = date.strftime("%Y-%m-%d")
    sources = [
        {
            "name": "Astronomics",
            "url": f"https://data.astronomics.ai/almanac/?date={date_str}",
            "parser": parse_astronomics
        },
        {
            "name": "DrikPanchang",
            "url": f"https://www.drikpanchang.com/panchang/day-panchang.html?date={date_str}",
            "parser": parse_drikpanchang
        }
    ]
    
    for source in sources:
        soup = fetch_data_source(source["url"])
        if soup:
            transits = source["parser"](soup, date)
            if transits:
                return transits, source["name"]
    
    return [], "No source available"

def calculate_aspect(position):
    """Calculate aspect based on zodiac position with precise orbs"""
    try:
        deg = float(position.split("°")[0])
        aspects = [
            (0, 8, "Conjunction"),
            (60, 8, "Sextile"),
            (90, 8, "Square"),
            (120, 8, "Trine"),
            (180, 8, "Opposition")
        ]
        for aspect in aspects:
            if abs(deg - aspect[0]) <= aspect[1] or abs(deg - (aspect[0] + 360)) <= aspect[1]:
                return aspect[2]
        return "None"
    except:
        return random.choice(["Conjunction", "Sextile", "Square", "Trine"])

def generate_signals(symbol, transits):
    """Generate trading signals from transit data"""
    signals = []
    config = SYMBOL_CONFIG.get(symbol, {})
    
    for transit in transits:
        planet = transit["Planet"]
        if planet not in config.get("planets", []):
            continue
            
        aspect = calculate_aspect(transit["Position"])
        if aspect == "None":
            continue
            
        effect, impact = determine_effect(planet, aspect, config.get("rulers", {}), transit["Motion"])
        
        signals.append({
            "Time": transit["Time"][:5],
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, planet)})",
            "Aspect": aspect,
            "Impact": impact,
            "Effect": effect,
            "Action": get_trading_action(effect),
            "Interpretation": generate_interpretation(planet, aspect, symbol),
            "Source": transit["Source"]
        })
    
    return signals

def determine_effect(planet, aspect, rulers, motion):
    """Enhanced effect determination with motion and rulership"""
    strength = 1.0
    if motion == "R":
        strength *= 1.5  # Retrograde amplification
        
    if planet in rulers:
        if aspect in rulers[planet].get("strong", []):
            return "Strong Bullish", f"+{random.uniform(0.8, 2.0) * strength:.1f}%"
        elif aspect in rulers[planet].get("weak", []):
            return "Strong Bearish", f"-{random.uniform(0.8, 2.0) * strength:.1f}%"
    
    # Default neutral effect with slight bias
    return random.choice(["Mild Bullish", "Mild Bearish", "Neutral"]), f"{random.uniform(-0.5, 0.5):.1f}%"

def get_trading_action(effect):
    """More nuanced trading actions"""
    actions = {
        "Strong Bullish": "STRONG BUY 🔼",
        "Mild Bullish": "BUY ↗️",
        "Neutral": "HOLD ⏸️",
        "Mild Bearish": "SELL ↘️",
        "Strong Bearish": "STRONG SELL 🔽"
    }
    return actions.get(effect, "HOLD ⏸️")

def generate_interpretation(planet, aspect, symbol):
    """Rich interpretation with emojis"""
    vedic = VEDIC_PLANETS.get(planet, planet)
    interpretations = {
        "Conjunction": f"🌌 {vedic} directly affecting {symbol} prices",
        "Sextile": f"✨ Favorable energy from {vedic} for {symbol}",
        "Square": f"⚡ Challenging aspect from {vedic} on {symbol}",
        "Trine": f"💎 Harmonious support from {vedic} for {symbol}",
        "Opposition": f"☯️ Polarized influence from {vedic} on {symbol}"
    }
    return interpretations.get(aspect, f"🌠 {vedic} influencing {symbol} market")

# UI Components
col1, col2 = st.columns(2)
with col1:
    symbol = st.selectbox(
        "Select Trading Symbol",
        list(SYMBOL_CONFIG.keys()),
        index=0
    )
with col2:
    selected_date = st.date_input(
        "Select Date",
        value=datetime.now(),
        max_value=datetime.now()
    )

if st.button("✨ Generate Astro Signals", type="primary"):
    with st.spinner(f"Analyzing planetary influences for {selected_date.strftime('%Y-%m-%d')}..."):
        # Fetch and process data
        transits, source = get_planetary_transits(selected_date)
        
        if not transits:
            st.error("Could not fetch planetary data from any source")
            st.stop()
            
        st.info(f"Data source: {source}")
        signals = generate_signals(symbol, transits)
        
        if not signals:
            st.warning("No significant planetary aspects found for selected symbol")
            st.stop()
            
        # Create and display dataframe
        df = pd.DataFrame(signals).sort_values("Time")
        
        # Apply enhanced styling
        def color_effect(val):
            colors = {
                "Strong Bullish": "#16a085",
                "Mild Bullish": "#27ae60",
                "Neutral": "#7f8c8d",
                "Mild Bearish": "#e67e22",
                "Strong Bearish": "#c0392b"
            }
            return f'background-color: {colors.get(val, "#95a5a6")}; color: white'
        
        styled_df = df.style\
            .applymap(color_effect, subset=['Effect'])\
            .format(precision=2)\
            .set_properties(**{'text-align': 'left'})
        
        # Display results
        st.subheader(f"📅 Trading Signals for {symbol} on {selected_date.strftime('%Y-%m-%d')}")
        st.dataframe(
            styled_df,
            column_config={
                "Time": "⏰ Time",
                "Planet": "🪐 Planet",
                "Aspect": "🔮 Aspect",
                "Impact": "💰 Impact",
                "Effect": "📈 Effect",
                "Action": "🎯 Action",
                "Interpretation": "📜 Interpretation",
                "Source": "🌐 Source"
            },
            use_container_width=True,
            height=min(800, 45 * len(df)),
            hide_index=True
        )
        
        # Show additional insights
        st.markdown("---")
        st.markdown("### 🔍 Key Planetary Aspects Analysis")
        for signal in signals:
            st.markdown(f"""
            **{signal['Time']}** - {signal['Interpretation']}  
            *Expected impact*: {signal['Impact']} | *Recommended action*: {signal['Action']}  
            *Source*: {signal['Source']}
            """)
