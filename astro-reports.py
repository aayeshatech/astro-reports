import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time as datetime_time
import logging

# Configure minimal logging for Streamlit Cloud
logging.basicConfig(level=logging.ERROR)  # Only log errors to avoid clutter
logger = logging.getLogger(__name__)

# Vedic planet names mapping
VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu",
    "Uranus": "Uranus", "Neptune": "Neptune", "Pluto": "Pluto"
}

# Basic symbol configuration for market analysis
SYMBOL_CONFIG = {
    "GOLD": {
        "planets": ["Sun", "Venus", "Saturn"],
        "rulers": {
            "Sun": {"strong": ["Trine", "Sextile"], "weak": ["Square", "Opposition"]},
            "Venus": {"strong": ["Trine", "Conjunction"], "weak": ["Square"]},
            "Saturn": {"strong": ["Conjunction"], "weak": ["Opposition"]}
        }
    },
    "SILVER": {
        "planets": ["Moon", "Venus"],
        "rulers": {
            "Moon": {"strong": ["Trine", "Sextile"], "weak": ["Square"]}
        }
    },
    "CRUDE": {
        "planets": ["Jupiter", "Neptune"],
        "rulers": {
            "Jupiter": {"strong": ["Trine"], "weak": ["Square"]}
        }
    },
    "NIFTY": {
        "planets": ["Sun", "Mars"],
        "rulers": {
            "Mars": {"strong": ["Conjunction"], "weak": ["Opposition"]}
        }
    }
}

# Nakshatra boost configuration for market impact
NAKSHATRA_BOOST = {
    "SILVER": {"Moon": ["Rohini", "Hasta", "Shravana"], "boost": 1.2},
    "GOLD": {"Sun": ["Krittika", "Uttara Phalguni"], "boost": 1.1},
    "CRUDE": {"Jupiter": ["Punarvasu", "Vishakha"], "boost": 1.1},
    "NIFTY": {"Mars": ["Mrigashira", "Dhanishta"], "boost": 1.1}
}

# Static monthly events for July 2024 (predefined data)
MONTHLY_EVENTS_2024 = [
    {"datetime": datetime(2024, 7, 2, 12, 0), "name": "Moon enters Rohini", "details": "Moon at 10° Taurus"},
    {"datetime": datetime(2024, 7, 4, 15, 30), "name": "Moon enters Mrigashira", "details": "Moon at 23° Gemini"},
    {"datetime": datetime(2024, 7, 6, 18, 45), "name": "Moon enters Ardra", "details": "Moon at 6° Cancer"}
]

# Static daily aspects for July 1, 2024 (predefined data)
DAILY_ASPECTS_2024 = [
    {"datetime": datetime(2024, 7, 1, 9, 15), "planet1": "Sun", "aspect": "Trine", "planet2": "Jupiter", "orb": "1°", "exact_time": "09:17"},
    {"datetime": datetime(2024, 7, 1, 14, 30), "planet1": "Moon", "aspect": "Sextile", "planet2": "Venus", "orb": "2°", "exact_time": "14:32"}
]

def calculate_effect(planet, aspect, rulers, symbol, nakshatra):
    """
    Calculates market effect based on planet, aspect, rulers, symbol, and nakshatra.
    Returns a tuple of effect label and impact percentage.
    """
    strength = 1.0
    nakshatra_boost = 1.0

    # Apply nakshatra boost if applicable
    if symbol in NAKSHATRA_BOOST and planet in NAKSHATRA_BOOST[symbol]:
        if nakshatra in NAKSHATRA_BOOST[symbol][planet]:
            nakshatra_boost = NAKSHATRA_BOOST[symbol]["boost"]

    # Check ruler-specific strong or weak aspects
    if planet in rulers:
        if aspect in rulers[planet].get("strong", []):
            return "Strong Bullish", f"+{1.2 * strength * nakshatra_boost:.2f}%"
        elif aspect in rulers[planet].get("weak", []):
            return "Strong Bearish", f"-{1.2 * strength / nakshatra_boost:.2f}%"

    # Default aspect-based effects
    bull_aspects = {"Conjunction", "Trine", "Sextile"}
    bear_aspects = {"Square", "Opposition"}

    if aspect in bull_aspects:
        return "Mild Bullish", f"+{0.5 * nakshatra_boost:.2f}%"
    elif aspect in bear_aspects:
        return "Mild Bearish", f"-{0.5 / nakshatra_boost:.2f}%"
    return "Neutral", "0.00%"

def get_trading_action(effect):
    """
    Maps market effect to a trading action.
    """
    mapping = {
        "Strong Bullish": "STRONG BUY",
        "Mild Bullish": "BUY",
        "Neutral": "HOLD",
        "Mild Bearish": "SELL",
        "Strong Bearish": "STRONG SELL"
    }
    return mapping.get(effect, "HOLD")

def generate_interpretation(planet, aspect, symbol, nakshatra):
    """
    Generates a textual interpretation of the trading signal.
    """
    vedic = VEDIC_PLANETS.get(planet, planet)
    interpretations = {
        "Conjunction": f"{vedic} directly influencing {symbol}",
        "Sextile": f"Favorable energy from {vedic} for {symbol}",
        "Square": f"Challenging aspect from {vedic} on {symbol}",
        "Trine": f"Harmonious support from {vedic} for {symbol}",
        "Opposition": f"Polarized influence from {vedic} on {symbol}"
    }
    base = interpretations.get(aspect, f"{vedic} impacting {symbol}")
    return f"{base} (Nakshatra: {nakshatra})"

def build_intraday_signals(symbol, aspects, monthly_events, user_start, user_end):
    """
    Builds intraday trading signals by combining Nakshatra and planetary aspects.
    Returns a sorted list of signal dictionaries.
    """
    signals = []
    rulers = SYMBOL_CONFIG[symbol]['rulers']
    planets_of_interest = set(SYMBOL_CONFIG[symbol]['planets'])

    # Extract Nakshatra change events
    nakshatra_events = []
    for event in monthly_events:
        if event['name'].lower().startswith('moon enters'):
            match = re.search(r"moon enters\s+([a-z-]+)", event['name'].lower())
            if match:
                nakshatra_name = match.group(1).replace('-', ' ').title()
                nakshatra_events.append({'dt': event['datetime'], 'nakshatra': nakshatra_name})

    # Sort and create Nakshatra time segments
    nakshatra_events.sort(key=lambda x: x['dt'])
    nakshatra_segments = []
    for i in range(len(nakshatra_events) - 1):
        nakshatra_segments.append({
            'start': nakshatra_events[i]['dt'],
            'end': nakshatra_events[i + 1]['dt'],
            'nakshatra': nakshatra_events[i]['nakshatra']
        })
    if nakshatra_events:
        nakshatra_segments.append({
            'start': nakshatra_events[-1]['dt'],
            'end': datetime.combine(user_start.date(), datetime_time.max),
            'nakshatra': nakshatra_events[-1]['nakshatra']
        })
    else:
        nakshatra_segments.append({
            'start': user_start,
            'end': user_end,
            'nakshatra': "Unknown"
        })

    # Generate signals for each aspect
    for aspect in aspects:
        dt = aspect['datetime']
        if not (user_start <= dt <= user_end):
            continue

        p1, p2 = aspect['planet1'], aspect['planet2']
        asp_type = aspect['aspect']

        if p1 not in planets_of_interest and p2 not in planets_of_interest:
            continue

        nakshatra = "Unknown"
        for segment in nakshatra_segments:
            if segment['start'] <= dt < segment['end']:
                nakshatra = segment['nakshatra']
                break

        planet = p1 if p1 in planets_of_interest else p2
        effect, impact = calculate_effect(planet, asp_type, rulers, symbol, nakshatra)
        action = get_trading_action(effect)
        interpretation = generate_interpretation(planet, asp_type, symbol, nakshatra)

        signals.append({
            "DateTime": dt,
            "Date": dt.date().strftime("%Y-%m-%d"),
            "Time": dt.strftime("%H:%M"),
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, planet)})",
            "Aspect": asp_type,
            "Nakshatra": nakshatra,
            "Effect": effect,
            "Impact": impact,
            "Action": action,
            "Interpretation": interpretation
        })

    return sorted(signals, key=lambda x: x["DateTime"])

def summarize_report(signals):
    """
    Summarizes trading signals into categories like bullish, bearish, etc.
    """
    bullish = sorted([f"{s['Date']} {s['Time']} ({s['Planet']})" for s in signals if 'Bullish' in s["Effect"]])
    bearish = sorted([f"{s['Date']} {s['Time']} ({s['Planet']})" for s in signals if 'Bearish' in s["Effect"]])
    reversals = []
    long_short = ["Long (Morning)", "Short (Evening)"]
    majors = sorted(set(s["Aspect"] for s in signals))
    return {
        "Bullish": bullish if bullish else ["No strong bullish events"],
        "Bearish": bearish if bearish else ["No strong bearish events"],
        "Reversals": reversals if reversals else ["No explicit reversals"],
        "Long/Short": long_short,
        "Major Aspects": majors if majors else ["None"]
    }

def main():
    """
    Main function to run the Streamlit app with user interface and signal generation.
    """
    st.title("🌌 Vedic Astro Trading Signals")
    st.markdown("Uses static data for July 2024. Select symbol and time range for analysis.")

    # Create input columns
    col1, col2, col3 = st.columns(3)
    with col1:
        symbol = st.selectbox("Select Symbol", list(SYMBOL_CONFIG.keys()), index=0)
    with col2:
        # Fixed to July 2024 range for static data
        selected_date = datetime(2024, 7, 1).date()
        selected_date = st.date_input("Select Date", value=selected_date, min_value=datetime(2024, 7, 1), max_value=datetime(2024, 7, 31))
    with col3:
        start_time = st.time_input("Select Start Time", value=datetime_time(0, 0))
        end_time = st.time_input("Select End Time", value=datetime_time(23, 59))

    # Validate time range
    if end_time <= start_time:
        st.warning("End time must be after start time. Please adjust.")
        return

    # Combine date and time for analysis range
    user_start = datetime.combine(selected_date, start_time)
    user_end = datetime.combine(selected_date, end_time)

    # Generate signals on button click
    if st.button("Generate Signals and Reports"):
        try:
            with st.spinner("Generating signals..."):
                # Use static data only
                monthly_events = MONTHLY_EVENTS_2024
                daily_aspects = [a for a in DAILY_ASPECTS_2024 if a["datetime"].date() == selected_date]

                # Check for available aspects
                if not daily_aspects:
                    st.warning("No aspects available for the selected date in static data.")
                    logger.warning(f"No aspects found for {selected_date}")
                    return

                # Build and validate signals
                signals = build_intraday_signals(symbol, daily_aspects, monthly_events, user_start, user_end)
                if not signals:
                    st.warning("No intraday trading signals generated for the selected range.")
                    logger.warning(f"No signals for {symbol} on {selected_date}")
                    return

                # Convert signals to DataFrame for display
                df_signals = pd.DataFrame(signals)

                # Define styling functions
                def color_effect(val):
                    return f"background-color: {'#27ae60' if 'Bullish' in val else '#e74c3c' if 'Bearish' in val else '#95a5a6'}; color: white;"

                def color_action(val):
                    return f"background-color: {'#16a085' if 'BUY' in val else '#c0392b' if 'SELL' in val else '#7f8c8d'}; color: white; font-weight: bold;"

                # Display signals table
                st.subheader(f"Intraday Signals for {symbol} on {selected_date.isoformat()}")
                st.dataframe(
                    df_signals.style.applymap(color_effect, subset=['Effect']).applymap(color_action, subset=['Action']).set_properties(**{'text-align': 'left'}),
                    use_container_width=True,
                    hide_index=True
                )

                # Generate summary reports
                daily_signals = [s for s in signals if s["Date"] == selected_date.strftime("%Y-%m-%d")]
                start_of_week = selected_date - timedelta(days=selected_date.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                weekly_signals = [s for s in signals if start_of_week <= datetime.strptime(s["Date"], "%Y-%m-%d").date() <= end_of_week]
                monthly_signals = [s for s in signals if datetime.strptime(s["Date"], "%Y-%m-%d").date().month == selected_date.month]

                daily_report = summarize_report(daily_signals)
                weekly_report = summarize_report(weekly_signals)
                monthly_report = summarize_report(monthly_signals)

                # Display reports in tabs
                st.subheader("Market Analysis Reports")
                tabs = st.tabs(["Daily", "Weekly", "Monthly"])
                with tabs[0]:
                    st.write("### Bullish Periods:")
                    st.write(", ".join(daily_report["Bullish"]))
                    st.write("### Bearish Periods:")
                    st.write(", ".join(daily_report["Bearish"]))
                    st.write("### Reversals:")
                    st.write(", ".join(daily_report["Reversals"]))
                    st.write("### Trading Strategy:")
                    st.write(", ".join(daily_report["Long/Short"]))
                    st.write("### Major Aspects:")
                    for aspect in daily_report["Major Aspects"]:
                        st.write(f"• {aspect}")

                with tabs[1]:
                    st.write("### Bullish Periods:")
                    st.write(", ".join(weekly_report["Bullish"]))
                    st.write("### Bearish Periods:")
                    st.write(", ".join(weekly_report["Bearish"]))
                    st.write("### Reversals:")
                    st.write(", ".join(weekly_report["Reversals"]))
                    st.write("### Trading Strategy:")
                    st.write(", ".join(weekly_report["Long/Short"]))
                    st.write("### Major Aspects:")
                    for aspect in weekly_report["Major Aspects"]:
                        st.write(f"• {aspect}")

                with tabs[2]:
                    st.write("### Bullish Periods:")
                    st.write(", ".join(monthly_report["Bullish"]))
                    st.write("### Bearish Periods:")
                    st.write(", ".join(monthly_report["Bearish"]))
                    st.write("### Reversals:")
                    st.write(", ".join(monthly_report["Reversals"]))
                    st.write("### Trading Strategy:")
                    st.write(", ".join(monthly_report["Long/Short"]))
                    st.write("### Major Aspects:")
                    for aspect in monthly_report["Major Aspects"]:
                        st.write(f"• {aspect}")

                st.success("Analysis completed successfully.")
                logger.info(f"Analysis completed for {symbol} on {selected_date}")

        except Exception as e:
            st.error(f"Error: {str(e)}. Please contact support at support@streamlit.io with the logs.")
            logger.error(f"Error in main: {str(e)}", exc_info=True)
            raise  # Re-raise for Streamlit Cloud to log the error

if __name__ == "__main__":
    main()
