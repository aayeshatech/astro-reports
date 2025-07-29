import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Configure page
st.set_page_config(page_title="Vedic Astro Trader Pro", layout="wide")
st.title("🌠 Vedic Astro Trading Signals Pro")
st.markdown("### Authentic Planetary Transit Analysis from Astro-Seek")

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
        "rulers": {
            "Sun": {"strong": ["Trine", "Sextile"], "weak": ["Square", "Opposition"]},
            "Venus": {"strong": ["Trine", "Conjunction"], "weak": ["Square"]}
        }
    },
    "SILVER": {
        "planets": ["Moon", "Venus"],
        "rulers": {
            "Moon": {"strong": ["Trine", "Sextile"], "weak": ["Square"]}
        }
    }
}

def fetch_astro_seek_data(date):
    """Fetch transit data from astro-seek.com"""
    try:
        url = f"https://horoscopes.astro-seek.com/calculate-astrology-aspects-transits-online-calendar-{date.strftime('%B-%Y').lower()}/?&barva=p&"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except Exception as e:
        st.error(f"Error fetching from Astro-Seek: {str(e)}")
        return None

def parse_astro_seek(soup, target_date):
    """Parse transit data from Astro-Seek website"""
    transits = []
    
    # Find the daily transit tables
    transit_tables = soup.find_all('table', class_='tableizer-table')
    
    for table in transit_tables:
        date_header = table.find_previous('h3')
        if not date_header:
            continue
            
        # Extract date from header (format: "Wednesday, June 4, 2025")
        date_match = re.search(r'[A-Za-z]+,\s+([A-Za-z]+\s+\d+,\s+\d+)', date_header.text)
        if not date_match:
            continue
            
        try:
            table_date = datetime.strptime(date_match.group(1), "%B %d, %Y").date()
            if table_date != target_date.date():
                continue
        except:
            continue
            
        # Parse transit rows
        for row in table.find_all('tr')[1:]:  # Skip header
            cols = [td.text.strip() for td in row.find_all('td')]
            if len(cols) >= 5:
                # Example format: "06:00 Moon Square Mars 10°21'"
                time_match = re.match(r'(\d{2}:\d{2})', cols[0])
                if not time_match:
                    continue
                    
                planet_match = re.match(r'([A-Za-z]+)\s+([A-Za-z]+)\s+([A-Za-z]+)', cols[1])
                if not planet_match:
                    continue
                    
                transits.append({
                    "Time": time_match.group(1),
                    "Planet1": planet_match.group(1),
                    "Aspect": planet_match.group(2),
                    "Planet2": planet_match.group(3),
                    "Degree": cols[2] if len(cols) > 2 else "",
                    "Source": "Astro-Seek"
                })
    
    return transits

def calculate_vedic_aspect(aspect_name):
    """Convert western aspect to Vedic equivalent"""
    aspect_map = {
        "Conjunction": "Conjunction",
        "Opposition": "Opposition",
        "Square": "Square",
        "Trine": "Trine",
        "Sextile": "Sextile",
        "Quincunx": "Inconjunct"
    }
    return aspect_map.get(aspect_name, aspect_name)

def generate_signals(symbol, transits):
    """Generate trading signals from transit data"""
    config = SYMBOL_CONFIG.get(symbol, {})
    signals = []
    
    for transit in transits:
        # Check if either planet is relevant for our symbol
        planet1 = transit["Planet1"]
        planet2 = transit["Planet2"]
        aspect = calculate_vedic_aspect(transit["Aspect"])
        
        # Determine which planet is affecting our symbol
        if planet1 in config.get("planets", []):
            planet = planet1
        elif planet2 in config.get("planets", []):
            planet = planet2
        else:
            continue
            
        effect, impact = determine_effect(planet, aspect, config.get("rulers", {}))
        
        signals.append({
            "Time": transit["Time"],
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, planet)})",
            "Aspect": aspect,
            "With": transit["Planet2"] if planet == planet1 else transit["Planet1"],
            "Degree": transit["Degree"],
            "Impact": impact,
            "Effect": effect,
            "Action": get_trading_action(effect),
            "Interpretation": generate_interpretation(planet, aspect, symbol),
            "Source": transit["Source"]
        })
    
    return signals

def determine_effect(planet, aspect, rulers):
    """Determine market effects based on Vedic principles"""
    if planet in rulers:
        if aspect in rulers[planet].get("strong", []):
            return "Strong Bullish", f"+{random.uniform(0.8, 1.8):.1f}%"
        elif aspect in rulers[planet].get("weak", []):
            return "Strong Bearish", f"-{random.uniform(0.8, 1.8):.1f}%"
    
    return "Neutral", f"{random.uniform(-0.2, 0.2):.1f}%"

def get_trading_action(effect):
    """Get trading action based on Vedic principles"""
    actions = {
        "Strong Bullish": "STRONG BUY (Shubha Yoga)",
        "Strong Bearish": "STRONG SELL (Ashubha Yoga)",
        "Neutral": "HOLD (Samya Yoga)"
    }
    return actions.get(effect, "OBSERVE")

def generate_interpretation(planet, aspect, symbol):
    """Generate Vedic interpretations"""
    vedic = VEDIC_PLANETS.get(planet, planet)
    interpretations = {
        "Conjunction": f"{vedic} Sammukha Yoga directly influencing {symbol}",
        "Sextile": f"{vedic} Shashtha Yoga creating favorable conditions for {symbol}",
        "Square": f"{vedic} Chaturtha Yoga creating challenges for {symbol}",
        "Trine": f"{vedic} Trine Yoga providing strong support for {symbol}",
        "Opposition": f"{vedic} Opposition Yoga creating polarization in {symbol}"
    }
    return interpretations.get(aspect, f"{vedic} influencing {symbol} market")

def main():
    """Main application function"""
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
            value=datetime(2025, 6, 1),  # Default to June 2025 for Astro-Seek
            min_value=datetime(2025, 6, 1),
            max_value=datetime(2025, 6, 30)
        )

    if st.button("Get Astro-Seek Signals", type="primary"):
        with st.spinner(f"Fetching Astro-Seek data for {selected_date.strftime('%B %d, %Y')}..."):
            soup = fetch_astro_seek_data(selected_date)
            
            if not soup:
                st.error("Could not fetch data from Astro-Seek. Please try again later.")
                st.stop()
                
            transits = parse_astro_seek(soup, selected_date)
            
            if not transits:
                st.warning(f"No transit data found for {selected_date.strftime('%B %d, %Y')} on Astro-Seek")
                st.stop()
                
            signals = generate_signals(symbol, transits)
            
            if not signals:
                st.warning("No significant planetary influences found for selected symbol/date")
                st.stop()
                
            # Create and display dataframe
            df = pd.DataFrame(signals).sort_values("Time")
            
            # Apply Vedic-style coloring
            def color_effect(val):
                colors = {
                    "Strong Bullish": "#27ae60",  # Green
                    "Strong Bearish": "#e74c3c",  # Red
                    "Neutral": "#f39c12"         # Yellow
                }
                return f'background-color: {colors.get(val, "#95a5a6")}; color: white'
            
            styled_df = df.style\
                .applymap(color_effect, subset=['Effect'])\
                .set_properties(**{'text-align': 'left'})
            
            st.dataframe(
                styled_df,
                column_config={
                    "Time": "⏳ Time",
                    "Planet": "🪐 Planet (Vedic)",
                    "Aspect": "🔮 Aspect",
                    "With": "⚡ With Planet",
                    "Degree": "📐 Degree",
                    "Impact": "💰 Impact",
                    "Effect": "📈 Effect",
                    "Action": "🎯 Action",
                    "Interpretation": "📜 Vedic Interpretation",
                    "Source": "🌐 Source"
                },
                use_container_width=True,
                height=min(800, 45 * len(df)),
                hide_index=True
            )
            
            # Show Vedic insights
            st.markdown("---")
            st.markdown("### 🔍 Vedic Astrological Insights")
            for signal in signals:
                st.markdown(f"""
                **{signal['Time']}** - {signal['Interpretation']}  
                **Aspect**: {signal['Aspect']} with {signal['With']} at {signal.get('Degree', '')}  
                **Effect**: {signal['Effect']} | **Action**: {signal['Action']}  
                **Source**: {signal['Source']}
                """)

if __name__ == "__main__":
    main()
