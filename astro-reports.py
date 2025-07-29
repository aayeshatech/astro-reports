import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta, date

# --- Config ---

VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu",
    "Uranus": "Uranus", "Neptune": "Neptune", "Pluto": "Pluto"
}

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

NAKSHATRA_BOOST = {
    "SILVER": {"Moon": ["Rohini", "Hasta", "Shravana"], "boost": 1.2},
    "GOLD": {"Sun": ["Krittika", "Uttara Phalguni"], "boost": 1.1},
    "CRUDE": {"Jupiter": ["Punarvasu", "Vishakha"], "boost": 1.1},
    "NIFTY": {"Mars": ["Mrigashira", "Dhanishta"], "boost": 1.1}
}

# --- Fallback data generator with date dependency for demo ---

def fetch_moon_nakshatra_segments(selected_date: date):
    """
    Simulate Nakshatra timing segments; this is a placeholder.
    You should replace it with real dynamic fetching/parsing per date.
    """
    base = datetime.combine(selected_date, time(0, 0))
    
    # Make date-dependent variables for demo variation
    seed = selected_date.day % 5
    
    # Sample Nakshatra lists to rotate through by day mod
    nakshatra_cycles = [
        [("Uttara Phalguni", 10), ("Hasta", 9), ("Chitra", 5)],   # Sum to 24 hours (10+9+5)
        [("Chitra", 8), ("Uttara Phalguni", 8), ("Hasta", 8)],
        [("Hasta", 12), ("Chitra", 6), ("Uttara Phalguni", 6)],
        [("Uttara Phalguni", 9), ("Hasta", 10), ("Chitra", 5)],
        [("Chitra", 7), ("Hasta", 11), ("Uttara Phalguni", 6)]
    ]
    
    cycle = nakshatra_cycles[seed]
    segments = []
    current = base
    for nakshatra_name, hours in cycle:
        end = current + timedelta(hours=hours)
        segments.append({"start": current, "end": end, "nakshatra": nakshatra_name})
        current = end
        if current.day != selected_date.day:
            # Do not cross to next day
            break
    return segments

# --- Aspect & effect calculations ---

def calculate_aspect_mock(planet, nakshatra, symbol):
    # Simple cyclic aspects (demo)
    code = abs(hash((planet, nakshatra, symbol))) % 3
    return ["Trine", "Square", "Conjunction"][code]

def determine_effect(planet, aspect, rulers, symbol, nakshatra):
    strength = 1.0
    nakshatra_boost = 1.0
    if symbol in NAKSHATRA_BOOST and planet in NAKSHATRA_BOOST[symbol]:
        if nakshatra in NAKSHATRA_BOOST[symbol][planet]:
            nakshatra_boost = NAKSHATRA_BOOST[symbol]["boost"]
    if planet in rulers:
        if aspect in rulers[planet].get("strong", []):
            return "Strong Bullish", f"+{1.2 * strength * nakshatra_boost:.1f}%"
        elif aspect in rulers[planet].get("weak", []):
            return "Strong Bearish", f"-{1.2 * strength / nakshatra_boost:.1f}%"
    if aspect == "Conjunction":
        return "Strong Bullish", f"+{1.1 * nakshatra_boost:.1f}%"
    elif aspect == "Square":
        return "Strong Bearish", f"-1.0%"
    else:
        return "Neutral", "0.0%"

def get_trading_action(effect):
    return {
        "Strong Bullish": "STRONG BUY",
        "Mild Bullish": "BUY",
        "Neutral": "HOLD",
        "Mild Bearish": "SELL",
        "Strong Bearish": "STRONG SELL"
    }.get(effect, "HOLD")

def generate_interpretation(planet, aspect, symbol, nakshatra):
    vedic = VEDIC_PLANETS.get(planet, planet)
    base = {
        "Conjunction": f"{vedic} directly influencing {symbol}",
        "Sextile": f"Favorable energy from {vedic} for {symbol}",
        "Square": f"Challenging aspect from {vedic} on {symbol}",
        "Trine": f"Harmonious support from {vedic} for {symbol}",
        "Opposition": f"Polarized influence from {vedic} on {symbol}"
    }.get(aspect, f"{vedic} affecting {symbol} market")
    return f"{base} (Nakshatra: {nakshatra})"

# --- Generate intraday signals ---

def generate_intraday_signals(symbol, moon_segments, start_dt, end_dt):
    config = SYMBOL_CONFIG[symbol]
    planet = config["planets"][0]
    signals = []
    for seg in moon_segments:
        seg_start = max(seg["start"], start_dt)
        seg_end = min(seg["end"], end_dt)
        if seg_end < start_dt or seg_start > end_dt:
            continue
        aspect = calculate_aspect_mock(planet, seg["nakshatra"], symbol)
        effect, impact = determine_effect(planet, aspect, config["rulers"], symbol, seg["nakshatra"])
        if effect not in {"Strong Bullish", "Strong Bearish"}:
            continue
        signals.append({
            "Date": seg_start.date().strftime("%Y-%m-%d"),
            "Time Window": f"{seg_start.strftime('%H:%M')} — {seg_end.strftime('%H:%M')}",
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, '')})",
            "Aspect": aspect,
            "Nakshatra": seg["nakshatra"],
            "Effect": effect,
            "Impact": impact,
            "Action": get_trading_action(effect),
            "Interpretation": generate_interpretation(planet, aspect, symbol, seg["nakshatra"])
        })
    return signals

# --- Generate dynamic daily, weekly, monthly reports ---

def filter_signals_for_day(signals, day):
    return [s for s in signals if s["Date"] == day.strftime("%Y-%m-%d")]

def filter_signals_for_week(signals, day):
    # Week: Monday to Sunday of the week containing day
    start_week = day - timedelta(days=day.weekday())
    end_week = start_week + timedelta(days=6)
    return [s for s in signals if start_week <= datetime.strptime(s["Date"], "%Y-%m-%d").date() <= end_week]

def filter_signals_for_month(signals, day):
    return [s for s in signals if datetime.strptime(s["Date"], "%Y-%m-%d").date().month == day.month and datetime.strptime(s["Date"], "%Y-%m-%d").date().year == day.year]

def summarize_report(signals):
    """Build simple report categories from signals"""
    bullish = [f"{s['Time Window']} ({s['Planet']})" for s in signals if s["Effect"] == "Strong Bullish"]
    bearish = [f"{s['Time Window']} ({s['Planet']})" for s in signals if s["Effect"] == "Strong Bearish"]
    reversals = []  # Add your reversal logic here if any
    long_short = ["Long (Morning)", "Short (Evening)"]  # Example placeholders
    major_aspects = list({s["Aspect"] for s in signals})  # Unique aspects as major aspects

    return {
        "Bullish": bullish if bullish else ["No strong bullish periods"],
        "Bearish": bearish if bearish else ["No strong bearish periods"],
        "Reversals": reversals if reversals else ["No clear reversals"],
        "Long/Short": long_short,
        "Major Aspects": major_aspects if major_aspects else ["No significant aspects"]
    }

# --- Main App ---

def main():
    st.title("🌌 Vedic Astro Trading Signals")
    st.markdown("### Select Symbol, Date, and Intraday Time Range")

    col1, col2, col3 = st.columns(3)
    with col1:
        symbol = st.selectbox("Select Symbol", list(SYMBOL_CONFIG.keys()))
    with col2:
        selected_date = st.date_input("Select Date", value=datetime.today())
    with col3:
        start_time = st.time_input("Select Start Time", value=time(0, 0))
        end_time = st.time_input("Select End Time", value=time(23, 59))

    start_dt = datetime.combine(selected_date, start_time)
    end_dt = datetime.combine(selected_date, end_time)
    if end_dt <= start_dt:
        st.warning("End time must be later than start time.")
        return

    if st.button("Generate Intraday Signals and Reports"):
        # Fetch Nakshatra segments (replace with real data fetch)
        moon_segments = fetch_moon_nakshatra_segments(selected_date)
        if not moon_segments:
            st.warning("No Moon Nakshatra transit data found for selected date.")
            return
        
        # Generate intraday signals for selected date/time range
        intraday_signals = generate_intraday_signals(symbol, moon_segments, start_dt, end_dt)

        if not intraday_signals:
            st.warning("No strong bullish/bearish planetary events found for selected symbol and time range.")
            return

        # Display intraday signals dataframe
        st.subheader(f"Intraday Signals for {symbol} on {selected_date.isoformat()}")
        df_intraday = pd.DataFrame(intraday_signals)
        def color_effect(val):
            return f"background-color: {'#27ae60' if val=='Strong Bullish' else '#e74c3c'}; color: white"
        def color_action(val):
            return f"background-color: {'#16a085' if val.startswith('STRONG BUY') else '#c0392b'}; color: white; font-weight: bold"
        styled = df_intraday.style.applymap(color_effect, subset=['Effect']).applymap(color_action, subset=['Action']).set_properties(**{'text-align': 'left'})
        st.dataframe(styled, use_container_width=True, hide_index=True)

        # Aggregate signals for full day, week, month reports
        # NOTE: For demo, generate intraday signals for full 24h as basis for aggregates
        full_day_start = datetime.combine(selected_date, time.min)
        full_day_end = datetime.combine(selected_date, time.max)
        full_day_signals = generate_intraday_signals(symbol, moon_segments, full_day_start, full_day_end)
        week_signals = generate_intraday_signals(symbol, moon_segments, full_day_start - timedelta(days=selected_date.weekday()), full_day_end + timedelta(days=6-selected_date.weekday()))
        month_signals = generate_intraday_signals(symbol, moon_segments, 
            datetime(selected_date.year, selected_date.month, 1, 0, 0), 
            datetime(selected_date.year, selected_date.month, 28, 23, 59))  # Approx month end, improve if desired

        # Generate summarized reports
        daily_report = summarize_report(filter_signals_for_day(full_day_signals, selected_date))
        weekly_report = summarize_report(filter_signals_for_week(full_day_signals, selected_date))
        monthly_report = summarize_report(filter_signals_for_month(full_day_signals, selected_date))

        # Show reports in tabs
        st.subheader("📈 Extended Market Analysis Reports")
        tabs = st.tabs(["Daily", "Weekly", "Monthly"])

        with tabs[0]:  # Daily
            st.write("### Bullish Periods:")
            st.write(", ".join(daily_report["Bullish"]))
            st.write("### Bearish Periods:")
            st.write(", ".join(daily_report["Bearish"]))
            st.write("### Reversal Times:")
            st.write(", ".join(daily_report["Reversals"]))
            st.write("### Trading Strategy:")
            st.write(", ".join(daily_report["Long/Short"]))
            st.write("### Major Aspects:")
            for aspect in daily_report["Major Aspects"]:
                st.write(f"• {aspect}")

        with tabs[1]:  # Weekly
            st.write("### Bullish Periods:")
            st.write(", ".join(weekly_report["Bullish"]))
            st.write("### Bearish Periods:")
            st.write(", ".join(weekly_report["Bearish"]))
            st.write("### Reversal Days:")
            st.write(", ".join(weekly_report["Reversals"]))
            st.write("### Trading Strategy:")
            st.write(", ".join(weekly_report["Long/Short"]))
            st.write("### Major Aspects:")
            for aspect in weekly_report["Major Aspects"]:
                st.write(f"• {aspect}")

        with tabs[2]:  # Monthly
            st.write("### Bullish Periods:")
            st.write(", ".join(monthly_report["Bullish"]))
            st.write("### Bearish Periods:")
            st.write(", ".join(monthly_report["Bearish"]))
            st.write("### Reversal Days:")
            st.write(", ".join(monthly_report["Reversals"]))
            st.write("### Trading Strategy:")
            st.write(", ".join(monthly_report["Long/Short"]))
            st.write("### Major Aspects:")
            for aspect in monthly_report["Major Aspects"]:
                st.write(f"• {aspect}")

        st.success("Analysis report generated. Replace fallback data with real transit data for full functionality.")

if __name__ == "__main__":
    main()
