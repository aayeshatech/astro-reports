import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import requests
from bs4 import BeautifulSoup
import re

# Vedic planets mapping
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
            "Saturn": {"strong": ["Conjunction"], "weak": ["Opposition"]},
        }
    },
    "SILVER": {
        "planets": ["Moon", "Venus"],
        "rulers": {
            "Moon": {"strong": ["Trine", "Sextile"], "weak": ["Square"]},
        }
    },
    "CRUDE": {
        "planets": ["Jupiter", "Neptune"],
        "rulers": {
            "Jupiter": {"strong": ["Trine"], "weak": ["Square"]},
        }
    },
    "NIFTY": {
        "planets": ["Sun", "Mars"],
        "rulers": {
            "Mars": {"strong": ["Conjunction"], "weak": ["Opposition"]},
        }
    }
}

NAKSHATRA_BOOST = {
    "SILVER": {"Moon": ["Rohini", "Hasta", "Shravana"], "boost": 1.2},
    "GOLD": {"Sun": ["Krittika", "Uttara Phalguni"], "boost": 1.1},
    "CRUDE": {"Jupiter": ["Punarvasu", "Vishakha"], "boost": 1.1},
    "NIFTY": {"Mars": ["Mrigashira", "Dhanishta"], "boost": 1.1},
}

# -- Parsing function to scrape Moon Nakshatra segments from AstroSeek --

def fetch_moon_nakshatra_segments_astoseek(date: datetime.date):
    """Fetch Moon Nakshatra transitions on AstroSeek for the whole month & return segments relevant for the given date."""
    # The AstroSeek Vedic Transit Calendar URL for month example (July 2025)
    base_url = "https://www.astro-seek.com/vedic-vedic-astrology-transit-calendar"

    # The site uses GET params to specify year/month, e.g. ?year=2025&month=7
    params = {
        "year": date.year,
        "month": date.month
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Find the transit calendar table - the table with class 'transit-calendar' or inspect the site for actual id/class
        # This selector works on current page structure (validate with browser dev tools)
        table = soup.find("table", {"class": "transit-calendar__table"})
        if table is None:
            st.warning("Unable to find transit calendar table on AstroSeek")
            return []

        moon_rows = []

        # Find all rows; each row corresponds to transit events for a day or time
        # Look for rows that mention "Moon" and a Nakshatra name with time for transit
        # The page describes Nakshatra transitions in either "Description" column or transit event columns

        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            # Column containing transit descriptions usually is consistent
            transit_desc = cols[2].get_text(strip=True)

            # Look for Moon Nakshatra entries in the description
            # Format example on AstroSeek: "Moon enters Hasta" or "Moon enters Chitra Nakshatra"
            # We'll parse all Moon Nakshatra entry times for the whole month

            # Use regex to detect lines like 'Moon enters <Nakshatra>'
            moon_nakshatra_match = re.search(r"Moon.*?enters\s+([A-Za-z-]+)", transit_desc, re.IGNORECASE)

            if moon_nakshatra_match:
                nakshatra_name = moon_nakshatra_match.group(1).strip()

                # Extract date & time from the row, usually first cols contain date/time info
                date_str = cols[0].get_text(strip=True)
                time_str = cols[1].get_text(strip=True)

                # Some dates might be day number only; infer full date from row or table header
                # AstroSeek uses day number, so we reconstruct full date (dd.mm.yyyy or dd/MM/yyyy)
                # The first col typically contains day of month number, e.g., '29'

                try:
                    day_int = int(date_str)
                    dt = datetime(date.year, date.month, day_int)
                    # parse time string e.g. '19:27'
                    time_obj = datetime.strptime(time_str, "%H:%M").time()
                    dt_with_time = datetime.combine(dt.date(), time_obj)
                except Exception as e:
                    continue

                # Only keep events for our selected date +/- 1 day for segment boundary formation
                if dt_with_time.date() == date or dt_with_time.date() == (date - timedelta(days=1)) or dt_with_time.date() == (date + timedelta(days=1)):
                    moon_rows.append({"dt": dt_with_time, "nakshatra": nakshatra_name})

        # Sort by datetime to order segments
        moon_rows.sort(key=lambda x: x["dt"])

        # Create segments spanning from one Nakshatra enter to next, clipping to selected date time range
        segments = []
        selected_date_start = datetime.combine(date, time.min)
        selected_date_end = datetime.combine(date, time.max)

        for i in range(len(moon_rows) - 1):
            start = moon_rows[i]
            end = moon_rows[i + 1]
            if end["dt"] <= selected_date_start or start["dt"] >= selected_date_end:
                continue

            segment_start = max(start["dt"], selected_date_start)
            segment_end = min(end["dt"], selected_date_end)

            segments.append({
                "start": segment_start,
                "end": segment_end,
                "nakshatra": start["nakshatra"]
            })

        # Handle last segment: from last Nakshatra until end of day
        if moon_rows:
            last = moon_rows[-1]
            if last["dt"] < selected_date_end:
                segments.append({
                    "start": max(last["dt"], selected_date_start),
                    "end": selected_date_end,
                    "nakshatra": last["nakshatra"]
                })
        else:
            return []

        return segments

    except Exception as e:
        st.error(f"Error fetching AstroSeek Nakshatra data: {e}")
        return []

# -- Aspect / effect simplification (demo only) --

def calculate_aspect_mock(planet, nakshatra, symbol):
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

# -- Signal generation --

def generate_intraday_signals(symbol, moon_segments, user_start_dt, user_end_dt):
    config = SYMBOL_CONFIG[symbol]
    planet = config["planets"][0]
    signals = []
    for seg in moon_segments:
        seg_start = seg["start"]
        seg_end = seg["end"]

        # Clip segment with user-selected time window
        start = max(seg_start, user_start_dt)
        end = min(seg_end, user_end_dt)

        if start >= end:
            continue

        aspect = calculate_aspect_mock(planet, seg["nakshatra"], symbol)
        effect, impact = determine_effect(planet, aspect, config["rulers"], symbol, seg["nakshatra"])

        if effect not in {"Strong Bullish", "Strong Bearish"}:
            continue

        signals.append({
            "Date": start.date().strftime("%Y-%m-%d"),
            "Time Window": f"{start.strftime('%H:%M')} — {end.strftime('%H:%M')}",
            "Planet": f"{planet} ({VEDIC_PLANETS.get(planet, '')})",
            "Aspect": aspect,
            "Nakshatra": seg["nakshatra"],
            "Effect": effect,
            "Impact": impact,
            "Action": get_trading_action(effect),
            "Interpretation": generate_interpretation(planet, aspect, symbol, seg["nakshatra"]),
        })

    return signals

# -- Helper functions for daily, weekly, monthly reports --

def filter_signals_for_day(signals, day):
    return [s for s in signals if s["Date"] == day.strftime("%Y-%m-%d")]

def filter_signals_for_week(signals, day):
    start_week = day - timedelta(days=day.weekday())
    end_week = start_week + timedelta(days=6)
    return [s for s in signals if start_week <= datetime.strptime(s["Date"], "%Y-%m-%d").date() <= end_week]

def filter_signals_for_month(signals, day):
    return [s for s in signals if datetime.strptime(s["Date"], "%Y-%m-%d").date().month == day.month and datetime.strptime(s["Date"], "%Y-%m-%d").date().year == day.year]

def summarize_report(signals):
    bullish = [f"{s['Time Window']} ({s['Planet']})" for s in signals if s["Effect"] == "Strong Bullish"]
    bearish = [f"{s['Time Window']} ({s['Planet']})" for s in signals if s["Effect"] == "Strong Bearish"]
    reversals = []  # Add your reversal logic if any
    long_short = ["Long (Morning)", "Short (Evening)"]  # Example placeholder
    major_aspects = list({s["Aspect"] for s in signals if s["Aspect"]}) or ["None"]

    return {
        "Bullish": bullish or ["No strong bullish periods"],
        "Bearish": bearish or ["No strong bearish periods"],
        "Reversals": reversals or ["No obvious reversals"],
        "Long/Short": long_short,
        "Major Aspects": major_aspects,
    }

# -- Streamlit UI ---

def main():
    st.title("🌌 Vedic Astro Trading Signals (AstroSeek Data)")
    st.markdown("Select Symbol, Date, and Time Range for intraday astro analysis.")

    col1, col2, col3 = st.columns(3)
    with col1:
        symbol = st.selectbox("Select Symbol", options=list(SYMBOL_CONFIG.keys()), index=0)
    with col2:
        selected_date = st.date_input("Select Date", value=datetime.now().date())
    with col3:
        start_time = st.time_input("Start Time", value=time(0, 0))
        end_time = st.time_input("End Time", value=time(23, 59))

    if end_time <= start_time:
        st.warning("End time must be later than start time.")
        return

    user_start_dt = datetime.combine(selected_date, start_time)
    user_end_dt = datetime.combine(selected_date, end_time)

    if st.button("Generate Intraday Signals and Reports"):
        st.info("Fetching Nakshatra transit segments from AstroSeek...")
        moon_segments = fetch_moon_nakshatra_segments_astoseek(selected_date)
        if not moon_segments:
            st.warning("No Moon Nakshatra transit data found for the selected date.")
            return

        signals = generate_intraday_signals(symbol, moon_segments, user_start_dt, user_end_dt)

        if not signals:
            st.warning("No strong bullish/bearish signals found for this date/time range and symbol.")
            return

        df = pd.DataFrame(signals)
        def color_effect(val):
            return f"background-color: {'#27ae60' if val=='Strong Bullish' else '#e74c3c'}; color: white"
        def color_action(val):
            return f"background-color: {'#16a085' if val.startswith('STRONG BUY') else '#c0392b'}; color: white; font-weight: bold"
        styled_df = df.style.applymap(color_effect, subset=["Effect"]).applymap(color_action, subset=["Action"]).set_properties(**{"text-align": "left"})

        st.subheader(f"Intraday Signals for {symbol} on {selected_date.isoformat()}")
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # Prepare reports for full day (00:00 - 23:59) for daily/weekly/monthly tabs
        full_day_start = datetime.combine(selected_date, time.min)
        full_day_end = datetime.combine(selected_date, time.max)
        full_day_signals = generate_intraday_signals(symbol, moon_segments, full_day_start, full_day_end)

        daily_report = summarize_report(filter_signals_for_day(full_day_signals, selected_date))
        weekly_report = summarize_report(filter_signals_for_week(full_day_signals, selected_date))
        monthly_report = summarize_report(filter_signals_for_month(full_day_signals, selected_date))

        st.subheader("📊 Market Analysis Summary Reports")
        tabs = st.tabs(["Daily", "Weekly", "Monthly"])

        with tabs[0]:
            st.write("### Bullish Periods:")
            st.write(", ".join(daily_report["Bullish"]))
            st.write("### Bearish Periods:")
            st.write(", ".join(daily_report["Bearish"]))
            st.write("### Reversal Times:")
            st.write(", ".join(daily_report["Reversals"]))
            st.write("### Trading Strategy:")
            st.write(", ".join(daily_report["Long/Short"]))
            st.write("### Major Aspects:")
            for asp in daily_report["Major Aspects"]:
                st.write(f"• {asp}")

        with tabs[1]:
            st.write("### Bullish Periods:")
            st.write(", ".join(weekly_report["Bullish"]))
            st.write("### Bearish Periods:")
            st.write(", ".join(weekly_report["Bearish"]))
            st.write("### Reversal Times:")
            st.write(", ".join(weekly_report["Reversals"]))
            st.write("### Trading Strategy:")
            st.write(", ".join(weekly_report["Long/Short"]))
            st.write("### Major Aspects:")
            for asp in weekly_report["Major Aspects"]:
                st.write(f"• {asp}")

        with tabs[2]:
            st.write("### Bullish Periods:")
            st.write(", ".join(monthly_report["Bullish"]))
            st.write("### Bearish Periods:")
            st.write(", ".join(monthly_report["Bearish"]))
            st.write("### Reversal Times:")
            st.write(", ".join(monthly_report["Reversals"]))
            st.write("### Trading Strategy:")
            st.write(", ".join(monthly_report["Long/Short"]))
            st.write("### Major Aspects:")
            for asp in monthly_report["Major Aspects"]:
                st.write(f"• {asp}")

        st.success("Signals and reports generated using AstroSeek Moon Nakshatra transit data.")

if __name__ == "__main__":
    main()
