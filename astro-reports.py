import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
import re
import time

# Vedic planet names mapping
VEDIC_PLANETS = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu",
    "Uranus": "Uranus", "Neptune": "Neptune", "Pluto": "Pluto"
}

# Basic symbol config (expand as needed)
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

# Nakshatra boost config
NAKSHATRA_BOOST = {
    "SILVER": {"Moon": ["Rohini", "Hasta", "Shravana"], "boost": 1.2},
    "GOLD": {"Sun": ["Krittika", "Uttara Phalguni"], "boost": 1.1},
    "CRUDE": {"Jupiter": ["Punarvasu", "Vishakha"], "boost": 1.1},
    "NIFTY": {"Mars": ["Mrigashira", "Dhanishta"], "boost": 1.1}
}

def fetch_monthly_astro_events(year, month):
    """
    Scrapes AstroSeek's Monthly Astro Calendar for major transit events for the month.
    Returns a list of dicts with 'datetime', 'name', and 'details'.
    """
    url = "https://horoscopes.astro-seek.com/monthly-astro-calendar"
    params = {"year": year, "month": month}
    events = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)

        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("table.table-striped tbody tr")

        if not rows:
            st.warning("No events found in the table. The website structure may have changed.")
            return events

        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) < 3:
                continue
            raw_date = tds[0].text.strip()  # e.g., "Jul 4, 2025, 12:44"
            event_name = tds[1].text.strip()
            details = tds[2].text.strip()
            try:
                dt = datetime.strptime(raw_date, "%b %d, %Y, %H:%M")
                events.append({
                    "datetime": dt,
                    "name": event_name,
                    "details": details
                })
            except ValueError as ve:
                st.warning(f"Failed to parse date '{raw_date}': {ve}")
                continue

    except requests.exceptions.RequestException as e:
        st.warning(f"Network error while fetching monthly astro events: {e}")
        return events
    except Exception as e:
        st.warning(f"Unexpected error while fetching monthly astro events: {e}")
        return events

    if not events:
        st.warning("No valid astro events were extracted. Using default Nakshatra.")
        # Fallback: Add a default event to avoid breaking Nakshatra logic
        events.append({
            "datetime": datetime(year, month, 1),
            "name": "Moon enters Unknown",
            "details": ""
        })

    return events

def fetch_daily_aspects(date_selected):
    """
    Scrapes AstroSeek's Astrology Aspects & Transits Online Calendar for aspects on selected date.
    Returns list of dicts with keys: 'datetime', 'planet1', 'aspect', 'planet2', 'orb', 'exact_time'.
    """
    url = "https://horoscopes.astro-seek.com/astrology-aspects-transits-online-calendar"
    aspects = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        rows = soup.select("table.table-striped tbody tr")

        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) < 6:
                continue

            raw_date_time = tds[0].text.strip()   # Format: "Jul 29, 2025, 17:30"
            try:
                dt = datetime.strptime(raw_date_time, "%b %d, %Y, %H:%M")
            except:
                continue

            if dt.date() != date_selected:
                continue

            planet1 = tds[1].text.strip()
            aspect = tds[2].text.strip()
            planet2 = tds[3].text.strip()
            orb = tds[4].text.strip()
            exact_time = tds[5].text.strip()

            aspects.append({
                "datetime": dt,
                "planet1": planet1,
                "aspect": aspect,
                "planet2": planet2,
                "orb": orb,
                "exact_time": exact_time
            })

    except Exception as e:
        st.warning(f"Error fetching daily aspects: {e}")
        return []

    return aspects

def calculate_effect(planet, aspect, rulers, symbol, nakshatra):
    """
    Determines market effect based on planet, aspect, rulers config, symbol and nakshatra.
    Returns effect label and impact percentage string.
    """
    strength = 1.0
    nakshatra_boost = 1.0

    if symbol in NAKSHATRA_BOOST and planet in NAKSHATRA_BOOST[symbol]:
        if nakshatra in NAKSHATRA_BOOST[symbol][planet]:
            nakshatra_boost = NAKSHATRA_BOOST[symbol]["boost"]

    if planet in rulers:
        if aspect in rulers[planet].get("strong", []):
            return "Strong Bullish", f"+{1.2 * strength * nakshatra_boost:.2f}%"
        elif aspect in rulers[planet].get("weak", []):
            return "Strong Bearish", f"-{1.2 * strength / nakshatra_boost:.2f}%"

    bull_aspects = {"Conjunction", "Trine", "Sextile"}
    bear_aspects = {"Square", "Opposition"}

    if aspect in bull_aspects:
        return "Mild Bullish", f"+{0.5 * nakshatra_boost:.2f}%"
    elif aspect in bear_aspects:
        return "Mild Bearish", f"-{0.5 / nakshatra_boost:.2f}%"
    else:
        return "Neutral", "0.00%"

def get_trading_action(effect):
    """
    Maps effect string to action label.
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
    Generates textual interpretation for the trading signal.
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
    Combines Moon Nakshatra and planetary aspects into intraday signals with impact analysis.
    Returns a sorted list of signal dicts.
    """
    signals = []
    rulers = SYMBOL_CONFIG[symbol]['rulers']
    planets_of_interest = set(SYMBOL_CONFIG[symbol]['planets'])

    # Extract Moon Nakshatra change events
    nakshatra_events = []
    for ev in monthly_events:
        if ev['name'].lower().startswith('moon enters'):
            m = re.search(r"moon enters\s+([a-z-]+)", ev['name'].lower())
            if m:
                nakshatra_name = m.group(1).replace('-', ' ').title()
                nakshatra_events.append({'dt': ev['datetime'], 'nakshatra': nakshatra_name})

    # Sort and create nakshatra time intervals
    nakshatra_events.sort(key=lambda x: x['dt'])
    nakshatra_segments = []
    for i in range(len(nakshatra_events) - 1):
        nakshatra_segments.append({
            'start': nakshatra_events[i]['dt'],
            'end': nakshatra_events[i+1]['dt'],
            'nakshatra': nakshatra_events[i]['nakshatra']
        })
    # Last segment till end of day
    if nakshatra_events:
        nakshatra_segments.append({
            'start': nakshatra_events[-1]['dt'],
            'end': datetime.combine(user_start.date(), time.max),
            'nakshatra': nakshatra_events[-1]['nakshatra']
        })
    else:
        # Fallback if no nakshatra events
        nakshatra_segments.append({
            'start': user_start,
            'end': user_end,
            'nakshatra': "Unknown"
        })

    for asp in aspects:
        dt = asp['datetime']
        if dt < user_start or dt > user_end:
            continue

        p1 = asp['planet1']
        p2 = asp['planet2']
        asp_type = asp['aspect']

        if p1 not in planets_of_interest and p2 not in planets_of_interest:
            continue

        nakshatra = "Unknown"
        for seg in nakshatra_segments:
            if seg['start'] <= dt < seg['end']:
                nakshatra = seg['nakshatra']
                break

        planet = p1 if p1 in planets_of_interest else p2
        effect, impact = calculate_effect(planet, asp_type, rulers, symbol, nakshatra)
        action = get_trading_action(effect)
        interp = generate_interpretation(planet, asp_type, symbol, nakshatra)

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
            "Interpretation": interp
        })

    signals.sort(key=lambda x: x["DateTime"])
    return signals

def summarize_report(signals):
    bullish = sorted([f"{s['Date']} {s['Time']} ({s['Planet']})" for s in signals if 'Bullish' in s["Effect"]])
    bearish = sorted([f"{s['Date']} {s['Time']} ({s['Planet']})" for s in signals if 'Bearish' in s["Effect"]])
    reversals = []  # Can implement logic later
    long_short = ["Long (Morning)", "Short (Evening)"]  # Placeholder
    majors = sorted(set(s["Aspect"] for s in signals))
    return {
        "Bullish": bullish or ["No strong bullish events"],
        "Bearish": bearish or ["No strong bearish events"],
        "Reversals": reversals or ["No explicit reversals"],
        "Long/Short": long_short,
        "Major Aspects": majors or ["None"]
    }

def main():
    st.title("🌌 Vedic Astro Trading Signals with AstroSeek Data")
    st.markdown("Select symbol, date, and intraday time range. Data fetched live from AstroSeek.com")

    col1, col2, col3 = st.columns(3)
    with col1:
        symbol = st.selectbox("Select Symbol", list(SYMBOL_CONFIG.keys()), index=0)
    with col2:
        selected_date = st.date_input("Select Date", value=datetime.today().date())
    with col3:
        start_time = st.time_input("Select Start Time", value=time(0, 0))
        end_time = st.time_input("Select End Time", value=time(23, 59))

    if end_time <= start_time:
        st.warning("End time must be after start time")
        return

    user_start = datetime.combine(selected_date, start_time)
    user_end = datetime.combine(selected_date, end_time)

    if st.button("Generate Signals and Reports"):
        st.info("Fetching monthly astro events (including Nakshatras) ...")
        monthly_events = fetch_monthly_astro_events(selected_date.year, selected_date.month)
        # No need for explicit error check here; function handles it with warnings

        st.info("Fetching daily planetary aspects and transits ...")
        daily_aspects = fetch_daily_aspects(selected_date)
        if not daily_aspects:
            st.warning("No planetary aspects found for this date.")
            return

        signals = build_intraday_signals(symbol, daily_aspects, monthly_events, user_start, user_end)
        if not signals:
            st.warning("No strong intraday trading signals found for this date/time.")
            return

        df_signals = pd.DataFrame(signals)

        def color_effect(val):
            return f"background-color: {'#27ae60' if 'Bullish' in val else '#e74c3c' if 'Bearish' in val else '#95a5a6'}; color: white;"
        def color_action(val):
            return f"background-color: {'#16a085' if 'BUY' in val else '#c0392b' if 'SELL' in val else '#7f8c8d'}; color: white; font-weight: bold;"

        st.subheader(f"Intraday Signals for {symbol} on {selected_date.isoformat()}")
        st.dataframe(
            df_signals.style.applymap(color_effect, subset=['Effect']).applymap(color_action, subset=['Action']).set_properties(**{'text-align': 'left'}),
            use_container_width=True,
            hide_index=True
        )

        # Summaries
        daily_signals = [s for s in signals if s["Date"] == selected_date.strftime("%Y-%m-%d")]
        start_of_week = selected_date - timedelta(days=selected_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        weekly_signals = [s for s in signals if start_of_week <= datetime.strptime(s["Date"], "%Y-%m-%d").date() <= end_of_week]
        monthly_signals = [s for s in signals if datetime.strptime(s["Date"], "%Y-%m-%d").date().month == selected_date.month and datetime.strptime(s["Date"], "%Y-%m-%d").date().year == selected_date.year]

        daily_report = summarize_report(daily_signals)
        weekly_report = summarize_report(weekly_signals)
        monthly_report = summarize_report(monthly_signals)

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
            for a in daily_report["Major Aspects"]:
                st.write(f"• {a}")

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
            for a in weekly_report["Major Aspects"]:
                st.write(f"• {a}")

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
            for a in monthly_report["Major Aspects"]:
                st.write(f"• {a}")

        st.success("Analysis complete.")

if __name__ == "__main__":
    main()
