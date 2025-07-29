import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
from bs4 import BeautifulSoup

# Configure page
st.set_page_config(page_title="Vedic Astro Trader", layout="wide")
st.title("💰 Vedic Astro Trading Signals")
st.markdown("### Planetary Influence on Financial Markets")

# Vedic Astrology Configuration
VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu"
}

# Trading symbol configurations
SYMBOL_CONFIG = {
    "GOLD": {
        "planets": ["Sun", "Venus", "Saturn"],
        "colors": {"bullish": "#FFD700", "bearish": "#B8860B"}
    },
    "SILVER": {
        "planets": ["Moon", "Venus"],
        "colors": {"bullish": "#C0C0C0", "bearish": "#808080"}
    },
    "CRUDE": {
        "planets": ["Jupiter", "Neptune"],
        "colors": {"bullish": "#FF4500", "bearish": "#8B0000"}
    },
    "NIFTY": {
        "planets": ["Sun", "Mars"],
        "colors": {"bullish": "#32CD32", "bearish": "#006400"}
    }
}

def fetch_astronomics_data(date):
    """Fetch planetary transit data from astronomics.ai"""
    try:
        url = f"https://data.astronomics.ai/almanac/?date={date.strftime('%Y-%m-%d')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'class': 'table'})
        
        if not table:
            st.warning("No transit table found on the page")
            return None
            
        transits = []
        for row in table.find_all('tr')[1:]:  # Skip header
            cols = row.find_all('td')
            if len(cols) >= 12:
                transits.append({
                    "Planet": cols[0].text.strip(),
                    "Time": cols[2].text.strip(),
                    "Zodiac": cols[7].text.strip(),
                    "Position": cols[10].text.strip(),
                    "Motion": cols[3].text.strip()
                })
        return transits if transits else None
        
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def generate_signals(symbol, transits):
    """Generate trading signals from transit data"""
    if not transits:
        return None
        
    signals = []
    symbol_planets = SYMBOL_CONFIG.get(symbol, {}).get("planets", [])
    
    for transit in transits:
        planet = transit["Planet"]
        if planet not in symbol_planets:
            continue
            
        time_str = transit["Time"][:5]  # HH:MM format
        aspect = determine_aspect(transit["Position"])
        effect, impact = determine_effect(planet, aspect, transit["Motion"])
        
        signals.append({
            "Time": time_str,
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, planet)})",
            "Aspect": aspect,
            "Impact": impact,
            "Effect": effect,
            "Action": get_trading_action(effect),
            "Interpretation": generate_interpretation(planet, aspect, symbol)
        })
    
    return signals if signals else None

def determine_aspect(position):
    """Determine astrological aspect from position"""
    try:
        deg = float(position.split("°")[0])
        aspects = [
            (0, "Conjunction"), (60, "Sextile"),
            (90, "Square"), (120, "Trine"),
            (180, "Opposition")
        ]
        closest = min(aspects, key=lambda x: abs(x[0] - deg % 30))
        return closest[1]
    except:
        return random.choice(["Conjunction", "Sextile", "Square", "Trine"])

def determine_effect(planet, aspect, motion):
    """Determine market effect of transit"""
    effect_map = {
        "Conjunction": ("Strong", 1.8),
        "Sextile": ("Mild", 0.8),
        "Square": ("Mild", -0.8),
        "Trine": ("Strong", 1.2),
        "Opposition": ("Strong", -1.5)
    }
    strength, base = effect_map.get(aspect, ("Neutral", 0))
    
    # Adjust for retrograde
    if motion == "R":
        base *= 1.5
        
    direction = "Bullish" if base > 0 else "Bearish"
    impact = f"{'+' if base > 0 else ''}{base:.1f}%"
    
    return f"{strength} {direction}", impact

def get_trading_action(effect):
    """Determine trading recommendation"""
    actions = {
        "Strong Bullish": "STRONG BUY",
        "Mild Bullish": "BUY",
        "Neutral": "HOLD",
        "Mild Bearish": "SELL",
        "Strong Bearish": "STRONG SELL"
    }
    return actions.get(effect, "HOLD")

def generate_interpretation(planet, aspect, symbol):
    """Create interpretation text"""
    vedic = VEDIC_PLANETS.get(planet, planet)
    interpretations = {
        "Conjunction": f"{vedic} directly influencing {symbol}",
        "Sextile": f"Favorable conditions from {vedic} for {symbol}",
        "Square": f"Challenges from {vedic} affecting {symbol}",
        "Trine": f"Harmonious support from {vedic} for {symbol}",
        "Opposition": f"Polarized energy from {vedic} impacting {symbol}"
    }
    return interpretations.get(aspect, f"{vedic} affecting {symbol}")

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

if st.button("Generate Trading Signals", type="primary"):
    with st.spinner(f"Analyzing planetary transits for {selected_date.strftime('%Y-%m-%d')}..."):
        # Fetch and process data
        transits = fetch_astronomics_data(selected_date)
        
        if transits is None:
            st.warning("Could not fetch transit data. Please try again later.")
            st.stop()
            
        signals = generate_signals(symbol, transits)
        
        if not signals:
            st.info("No significant planetary influences found for selected symbol/date")
            st.stop()
            
        # Create and display dataframe
        df = pd.DataFrame(signals)
        
        # Apply styling
        def color_effect(val):
            colors = {
                "Strong Bullish": SYMBOL_CONFIG[symbol]["colors"]["bullish"],
                "Mild Bullish": lighten_color(SYMBOL_CONFIG[symbol]["colors"]["bullish"], 0.7),
                "Neutral": "#7f8c8d",
                "Mild Bearish": lighten_color(SYMBOL_CONFIG[symbol]["colors"]["bearish"], 0.7),
                "Strong Bearish": SYMBOL_CONFIG[symbol]["colors"]["bearish"]
            }
            return f'background-color: {colors.get(val, "#95a5a6")}; color: white'
        
        def color_action(val):
            colors = {
                "STRONG BUY": "#27ae60",
                "BUY": "#2ecc71",
                "HOLD": "#7f8c8d",
                "SELL": "#e67e22",
                "STRONG SELL": "#c0392b"
            }
            return f'background-color: {colors.get(val, "#95a5a6")}; color: white; font-weight: bold'
        
        styled_df = df.style\
            .applymap(color_effect, subset=['Effect'])\
            .applymap(color_action, subset=['Action'])\
            .format(precision=2)\
            .set_properties(**{'text-align': 'left'})
        
        # Display results
        st.subheader(f"Trading Signals for {symbol} on {selected_date.strftime('%Y-%m-%d')}")
        st.dataframe(
            styled_df,
            column_config={
                "Time": "Time (24h)",
                "Planet": "Planet (Vedic)",
                "Aspect": "Aspect",
                "Impact": "Price Impact",
                "Effect": "Market Effect",
                "Action": "Trading Action",
                "Interpretation": "Astrological Interpretation"
            },
            use_container_width=True,
            height=min(800, 45 * len(df)),
            hide_index=True
        )
        
        # Show additional insights
        st.markdown("---")
        st.markdown("### Key Planetary Influences Today")
        for signal in signals:
            st.markdown(f"**{signal['Time']}** - {signal['Interpretation']} (Expected impact: {signal['Impact']})")

def lighten_color(color, factor=0.5):
    """Lighten color by factor (0-1)"""
    try:
        import matplotlib.colors as mc
        import colorsys
        c = mc.cnames.get(color, color)
        c = colorsys.rgb_to_hls(*mc.to_rgb(c))
        return colorsys.hls_to_rgb(c[0], 1 - factor * (1 - c[1]), c[2])
    except:
        return color
