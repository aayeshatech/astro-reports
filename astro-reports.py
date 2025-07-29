import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import random

# Vedic Astrology Configuration
VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu"
}

# Planetary effects for different symbols
SYMBOL_RULERSHIPS = {
    "GOLD": {
        "Sun": {"strong": ["Trine", "Sextile"], "weak": ["Square", "Opposition"]},
        "Venus": {"strong": ["Trine", "Conjunction"], "weak": ["Square"]},
        "Saturn": {"strong": [], "weak": ["Conjunction", "Opposition"]}
    },
    "SILVER": {
        "Moon": {"strong": ["Trine", "Sextile"], "weak": ["Square"]},
        "Venus": {"strong": ["Conjunction"], "weak": ["Opposition"]}
    },
    "CRUDE": {
        "Jupiter": {"strong": ["Trine"], "weak": ["Square"]},
        "Neptune": {"strong": ["Sextile"], "weak": ["Opposition"]}
    },
    "NIFTY": {
        "Sun": {"strong": ["Trine"], "weak": ["Square"]},
        "Mars": {"strong": ["Conjunction"], "weak": ["Opposition"]}
    }
}

# Sample planetary transit data (would normally fetch from API)
SAMPLE_TRANSITS = [
    {"Planet": "Moon", "Date": "2025-07-29", "Time": "02:11:15", "Motion": "D", "Sign Lord": "Me", "Star Lord": "Su", "Sub Lord": "Ju", "Zodiac": "Virgo", "Nakshatra": "Uttaraphalguni", "Pada": 2, "Pos in Zodiac": "01°13'20\"", "Declination": 1.32},
    {"Planet": "Moon", "Date": "2025-07-29", "Time": "05:37:44", "Motion": "D", "Sign Lord": "Me", "Star Lord": "Su", "Sub Lord": "Sa", "Zodiac": "Virgo", "Nakshatra": "Uttaraphalguni", "Pada": 2, "Pos in Zodiac": "03°00'00\"", "Declination": 0.47},
    {"Planet": "Sun", "Date": "2025-07-29", "Time": "07:34:55", "Motion": "D", "Sign Lord": "Mo", "Star Lord": "Sa", "Sub Lord": "Ma", "Zodiac": "Cancer", "Nakshatra": "Pushya", "Pada": 3, "Pos in Zodiac": "12°06'40\"", "Declination": 18.71},
    {"Planet": "Moon", "Date": "2025-07-29", "Time": "09:43:47", "Motion": "D", "Sign Lord": "Me", "Star Lord": "Su", "Sub Lord": "Me", "Zodiac": "Virgo", "Nakshatra": "Uttaraphalguni", "Pada": 3, "Pos in Zodiac": "05°06'40\"", "Declination": -0.54},
    {"Planet": "Moon", "Date": "2025-07-29", "Time": "13:24:44", "Motion": "D", "Sign Lord": "Me", "Star Lord": "Su", "Sub Lord": "Ke", "Zodiac": "Virgo", "Nakshatra": "Uttaraphalguni", "Pada": 4, "Pos in Zodiac": "07°00'00\"", "Declination": -1.44},
    {"Planet": "Moon", "Date": "2025-07-29", "Time": "14:55:55", "Motion": "D", "Sign Lord": "Me", "Star Lord": "Su", "Sub Lord": "Ve", "Zodiac": "Virgo", "Nakshatra": "Uttaraphalguni", "Pada": 4, "Pos in Zodiac": "07°46'40\"", "Declination": -1.82},
    {"Planet": "Moon", "Date": "2025-07-29", "Time": "19:17:06", "Motion": "D", "Sign Lord": "Me", "Star Lord": "Mo", "Sub Lord": "Mo", "Zodiac": "Virgo", "Nakshatra": "Hasta", "Pada": 1, "Pos in Zodiac": "10°00'00\"", "Declination": -2.88},
    {"Planet": "Mercury", "Date": "2025-07-29", "Time": "19:29:08", "Motion": "R", "Sign Lord": "Mo", "Star Lord": "Sa", "Sub Lord": "Ju", "Zodiac": "Cancer", "Nakshatra": "Pushya", "Pada": 4, "Pos in Zodiac": "16°39'59\"", "Declination": 12.76},
    {"Planet": "Moon", "Date": "2025-07-29", "Time": "21:28:02", "Motion": "D", "Sign Lord": "Me", "Star Lord": "Mo", "Sub Lord": "Ma", "Zodiac": "Virgo", "Nakshatra": "Hasta", "Pada": 1, "Pos in Zodiac": "11°06'40\"", "Declination": -3.41},
    {"Planet": "Moon", "Date": "2025-07-29", "Time": "22:59:50", "Motion": "D", "Sign Lord": "Me", "Star Lord": "Mo", "Sub Lord": "Ra", "Zodiac": "Virgo", "Nakshatra": "Hasta", "Pada": 1, "Pos in Zodiac": "11°53'20\"", "Declination": -3.78}
]

def get_aspect_for_position(planet, zodiac_pos):
    """Determine aspect based on zodiac position (simplified)"""
    try:
        degree = float(zodiac_pos.split('°')[0])
    except:
        degree = random.randint(0, 30)
    
    # Simplified aspect determination based on degree
    if degree % 30 == 0:
        return "Conjunction"
    elif degree % 60 == 0:
        return "Sextile"
    elif degree % 90 == 0:
        return "Square"
    elif degree % 120 == 0:
        return "Trine"
    elif degree % 180 == 0:
        return "Opposition"
    else:
        # If no major aspect, choose based on motion and declination
        return random.choice(["Sextile", "Square", "Trine"])

def generate_transits_from_actual_data(symbol, selected_date):
    """Generate transits based on actual planetary data"""
    transits = []
    
    # Convert selected_date to string format matching sample data
    selected_date_str = selected_date.strftime("%Y-%m-%d")
    
    # Filter transits for selected date
    daily_transits = [t for t in SAMPLE_TRANSITS if t["Date"] == selected_date_str]
    
    if not daily_transits:
        st.warning(f"No transit data available for {selected_date_str}")
        return pd.DataFrame()
    
    # Get rulerships for the selected symbol
    planetary_effects = SYMBOL_RULERSHIPS.get(symbol, {})
    
    for transit in daily_transits:
        planet = transit["Planet"]
        time_str = transit["Time"][:5]  # Get HH:MM format
        
        # Determine aspect based on position
        aspect = get_aspect_for_position(planet, transit["Pos in Zodiac"])
        
        # Determine market effect
        effect, impact = determine_effect(planet, aspect, planetary_effects)
        interpretation = generate_interpretation(planet, aspect, symbol)
        
        transits.append({
            "Time": time_str,
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, planet)})",
            "Aspect": aspect,
            "Impact": impact,
            "Effect": effect,
            "Action": get_action(effect),
            "Interpretation": interpretation
        })
    
    return pd.DataFrame(transits)

def determine_effect(planet, aspect, planetary_effects):
    """Determine market effect based on planetary aspects"""
    if planet in planetary_effects:
        if aspect in planetary_effects[planet]["strong"]:
            effect = "Strong Bullish"
            impact = f"+{random.uniform(0.8, 2.0):.1f}%"
        elif aspect in planetary_effects[planet]["weak"]:
            effect = "Strong Bearish"
            impact = f"-{random.uniform(0.8, 2.0):.1f}%"
        else:
            effect = "Neutral"
            impact = f"{random.uniform(-0.5, 0.5):.1f}%"
    else:
        # Default effect based on motion (D=Direct, R=Retrograde)
        effect = "Mild Bullish" if random.random() > 0.5 else "Mild Bearish"
        impact = f"{random.uniform(-0.7, 0.7):.1f}%"
    return effect, impact

def get_action(effect):
    """Determine trading action based on effect"""
    if "Strong Bullish" in effect:
        return "GO LONG"
    elif "Mild Bullish" in effect:
        return "Consider LONG"
    elif "Strong Bearish" in effect:
        return "GO SHORT"
    elif "Mild Bearish" in effect:
        return "Consider SHORT"
    return "HOLD"

def generate_interpretation(planet, aspect, symbol):
    """Generate interpretation for any symbol"""
    vedic_name = VEDIC_PLANETS.get(planet, planet)
    action_words = {
        "Conjunction": "influencing",
        "Sextile": "supporting",
        "Square": "pressuring",
        "Trine": "benefiting",
        "Opposition": "challenging"
    }
    return f"{vedic_name}'s {aspect.lower()} {action_words[aspect]} {symbol.lower()} market"

# Streamlit App
def main():
    st.title("Vedic Astro Trading Signals - Actual Transits")
    
    # Symbol input section
    st.subheader("Symbol Selection")
    symbol = st.text_input("Enter Symbol (e.g., GOLD, BTC, NIFTY)", "GOLD").strip().upper()
    
    # Date selection - default to date we have sample data for
    st.subheader("Analysis Date")
    selected_date = st.date_input("Select Date", value=datetime(2025, 7, 29))
    
    if st.button("Generate Astro Trading Report"):
        if not symbol:
            st.warning("Please enter a symbol")
            return
            
        with st.spinner(f"Generating Vedic astrology report for {symbol} on {selected_date.strftime('%Y-%m-%d')}..."):
            transit_df = generate_transits_from_actual_data(symbol, selected_date)
            
            if transit_df.empty:
                st.warning("No transit data available for the selected date")
                return
            
            # Apply styling
            def color_effect(val):
                colors = {
                    "Strong Bullish": "#27AE60",
                    "Mild Bullish": "#58D68D",
                    "Neutral": "#95A5A6",
                    "Mild Bearish": "#E74C3C",
                    "Strong Bearish": "#C0392B"
                }
                return f'background-color: {colors.get(val, "#95A5A6")}; color: white'
            
            def color_action(val):
                colors = {
                    "GO LONG": "#27AE60",
                    "Consider LONG": "#2ECC71",
                    "HOLD": "#95A5A6",
                    "Consider SHORT": "#E74C3C",
                    "GO SHORT": "#C0392B"
                }
                return f'background-color: {colors.get(val, "#95A5A6")}; color: white; font-weight: bold'
            
            try:
                styled_df = transit_df.style\
                    .applymap(color_effect, subset=['Effect'])\
                    .applymap(color_action, subset=['Action'])\
                    .set_properties(**{'text-align': 'left'})
                
                # Display the dataframe
                st.dataframe(
                    styled_df,
                    column_config={
                        "Time": "Time (24h)",
                        "Planet": "Planet (Vedic)",
                        "Aspect": "Aspect",
                        "Impact": "Price Impact",
                        "Effect": "Market Effect",
                        "Action": "Trading Action",
                        "Interpretation": "Astro Interpretation"
                    },
                    use_container_width=True,
                    height=min(800, 35 * len(transit_df)),
                    hide_index=True
                )
            except Exception as e:
                st.error(f"Error displaying data: {str(e)}")
                st.write("Raw data for debugging:")
                st.write(transit_df)

if __name__ == "__main__":
    main()
