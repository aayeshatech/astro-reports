import streamlit as st
import pandas as pd

# Configure page
st.set_page_config(page_title="Vedic Astro Trader", layout="wide")
st.title("🌌 Vedic Astro Trading Signals")
st.markdown("### Intraday Timing Analysis (IST)")

# Hardcoded intraday transit data for July 29, 2025
intraday_transits = [
    {"Date": "2025-07-29", "Time": "00:00", "Planet": "Sun (Surya)", "Aspect": "Square", "Nakshatra": "Krittika", "Impact": "-0.2%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Challenging aspect from Surya on GOLD (Nakshatra: Krittika)"},
    {"Date": "2025-07-29", "Time": "00:00", "Planet": "Moon (Chandra)", "Aspect": "Trine", "Nakshatra": "Rohini", "Impact": "+0.4%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Chandra for GOLD (Nakshatra: Rohini)"},
    {"Date": "2025-07-29", "Time": "01:00", "Planet": "Mercury (Budha)", "Aspect": "Sextile", "Nakshatra": "Hasta", "Impact": "+0.3%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Favorable energy from Budha for GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "01:00", "Planet": "Venus (Shukra)", "Aspect": "Opposition", "Nakshatra": "Uttara Phalguni", "Impact": "-0.5%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Polarized influence from Shukra on GOLD (Nakshatra: Uttara Phalguni)"},
    {"Date": "2025-07-29", "Time": "02:00", "Planet": "Mars (Mangala)", "Aspect": "Square", "Nakshatra": "Mrigashira", "Impact": "-0.3%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Challenging aspect from Mangala on GOLD (Nakshatra: Mrigashira)"},
    {"Date": "2025-07-29", "Time": "02:00", "Planet": "Jupiter (Guru)", "Aspect": "Trine", "Nakshatra": "Punarvasu", "Impact": "+0.6%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Guru for GOLD (Nakshatra: Punarvasu)"},
    {"Date": "2025-07-29", "Time": "03:00", "Planet": "Saturn (Shani)", "Aspect": "Sextile", "Nakshatra": "Hasta", "Impact": "+0.4%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Favorable energy from Shani for GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "03:00", "Planet": "Uranus (Uranus)", "Aspect": "Conjunction", "Nakshatra": "Hasta", "Impact": "0.0%", "Effect": "Neutral", "Action": "HOLD", "Interpretation": "Uranus directly influencing GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "04:00", "Planet": "Neptune (Neptune)", "Aspect": "Opposition", "Nakshatra": "Hasta", "Impact": "-0.1%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Polarized influence from Neptune on GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "04:00", "Planet": "Pluto (Pluto)", "Aspect": "Trine", "Nakshatra": "Hasta", "Impact": "+0.2%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Pluto for GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "05:00", "Planet": "Sun (Surya)", "Aspect": "Trine", "Nakshatra": "Krittika", "Impact": "+0.5%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Surya for GOLD (Nakshatra: Krittika)"},
    {"Date": "2025-07-29", "Time": "05:00", "Planet": "Moon (Chandra)", "Aspect": "Sextile", "Nakshatra": "Rohini", "Impact": "+0.3%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Favorable energy from Chandra for GOLD (Nakshatra: Rohini)"},
    {"Date": "2025-07-29", "Time": "06:00", "Planet": "Mercury (Budha)", "Aspect": "Square", "Nakshatra": "Hasta", "Impact": "-0.4%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Challenging aspect from Budha on GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "06:00", "Planet": "Venus (Shukra)", "Aspect": "Conjunction", "Nakshatra": "Uttara Phalguni", "Impact": "+1.2%", "Effect": "Strong Bullish", "Action": "STRONG BUY", "Interpretation": "Shukra directly influencing GOLD (Nakshatra: Uttara Phalguni)"},
    {"Date": "2025-07-29", "Time": "07:00", "Planet": "Mars (Mangala)", "Aspect": "Sextile", "Nakshatra": "Mrigashira", "Impact": "+0.2%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Favorable energy from Mangala for GOLD (Nakshatra: Mrigashira)"},
    {"Date": "2025-07-29", "Time": "07:00", "Planet": "Jupiter (Guru)", "Aspect": "Trine", "Nakshatra": "Punarvasu", "Impact": "+0.7%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Guru for GOLD (Nakshatra: Punarvasu)"},
    {"Date": "2025-07-29", "Time": "08:00", "Planet": "Saturn (Shani)", "Aspect": "Opposition", "Nakshatra": "Hasta", "Impact": "-0.3%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Polarized influence from Shani on GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "08:00", "Planet": "Uranus (Uranus)", "Aspect": "Square", "Nakshatra": "Hasta", "Impact": "-0.2%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Challenging aspect from Uranus on GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "09:00", "Planet": "Neptune (Neptune)", "Aspect": "Trine", "Nakshatra": "Hasta", "Impact": "+0.1%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Neptune for GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "09:00", "Planet": "Pluto (Pluto)", "Aspect": "Sextile", "Nakshatra": "Hasta", "Impact": "+0.3%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Favorable energy from Pluto for GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "10:00", "Planet": "Sun (Surya)", "Aspect": "Conjunction", "Nakshatra": "Krittika", "Impact": "+0.4%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Surya directly influencing GOLD (Nakshatra: Krittika)"},
    {"Date": "2025-07-29", "Time": "10:00", "Planet": "Moon (Chandra)", "Aspect": "Square", "Nakshatra": "Rohini", "Impact": "-0.2%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Challenging aspect from Chandra on GOLD (Nakshatra: Rohini)"},
    {"Date": "2025-07-29", "Time": "11:00", "Planet": "Mercury (Budha)", "Aspect": "Trine", "Nakshatra": "Hasta", "Impact": "+0.5%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Budha for GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "11:00", "Planet": "Venus (Shukra)", "Aspect": "Sextile", "Nakshatra": "Uttara Phalguni", "Impact": "+0.6%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Favorable energy from Shukra for GOLD (Nakshatra: Uttara Phalguni)"},
    {"Date": "2025-07-29", "Time": "12:00", "Planet": "Mars (Mangala)", "Aspect": "Opposition", "Nakshatra": "Mrigashira", "Impact": "-0.4%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Polarized influence from Mangala on GOLD (Nakshatra: Mrigashira)"},
    {"Date": "2025-07-29", "Time": "12:00", "Planet": "Jupiter (Guru)", "Aspect": "Conjunction", "Nakshatra": "Punarvasu", "Impact": "+0.8%", "Effect": "Strong Bullish", "Action": "STRONG BUY", "Interpretation": "Guru directly influencing GOLD (Nakshatra: Punarvasu)"},
    {"Date": "2025-07-29", "Time": "13:00", "Planet": "Saturn (Shani)", "Aspect": "Trine", "Nakshatra": "Hasta", "Impact": "+0.3%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Shani for GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "13:00", "Planet": "Uranus (Uranus)", "Aspect": "Sextile", "Nakshatra": "Hasta", "Impact": "+0.2%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Favorable energy from Uranus for GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "14:00", "Planet": "Neptune (Neptune)", "Aspect": "Square", "Nakshatra": "Hasta", "Impact": "-0.3%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Challenging aspect from Neptune on GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "14:00", "Planet": "Pluto (Pluto)", "Aspect": "Conjunction", "Nakshatra": "Hasta", "Impact": "+0.1%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Pluto directly influencing GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "15:00", "Planet": "Sun (Surya)", "Aspect": "Sextile", "Nakshatra": "Krittika", "Impact": "+0.4%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Favorable energy from Surya for GOLD (Nakshatra: Krittika)"},
    {"Date": "2025-07-29", "Time": "15:00", "Planet": "Moon (Chandra)", "Aspect": "Trine", "Nakshatra": "Rohini", "Impact": "+0.5%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Chandra for GOLD (Nakshatra: Rohini)"},
    {"Date": "2025-07-29", "Time": "16:00", "Planet": "Mercury (Budha)", "Aspect": "Opposition", "Nakshatra": "Hasta", "Impact": "-0.3%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Polarized influence from Budha on GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "16:00", "Planet": "Venus (Shukra)", "Aspect": "Trine", "Nakshatra": "Uttara Phalguni", "Impact": "+0.7%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Shukra for GOLD (Nakshatra: Uttara Phalguni)"},
    {"Date": "2025-07-29", "Time": "17:00", "Planet": "Mars (Mangala)", "Aspect": "Sextile", "Nakshatra": "Mrigashira", "Impact": "+0.2%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Favorable energy from Mangala for GOLD (Nakshatra: Mrigashira)"},
    {"Date": "2025-07-29", "Time": "17:00", "Planet": "Jupiter (Guru)", "Aspect": "Square", "Nakshatra": "Punarvasu", "Impact": "-0.2%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Challenging aspect from Guru on GOLD (Nakshatra: Punarvasu)"},
    {"Date": "2025-07-29", "Time": "17:30", "Planet": "Saturn (Shani)", "Aspect": "Conjunction", "Nakshatra": "Hasta", "Impact": "0.0%", "Effect": "Neutral", "Action": "HOLD", "Interpretation": "Shani directly influencing GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "17:30", "Planet": "Uranus (Uranus)", "Aspect": "Conjunction", "Nakshatra": "Hasta", "Impact": "0.0%", "Effect": "Neutral", "Action": "HOLD", "Interpretation": "Uranus directly influencing GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "17:30", "Planet": "Saturn (Shani)", "Aspect": "Conjunction", "Nakshatra": "Hasta", "Impact": "0.0%", "Effect": "Neutral", "Action": "HOLD", "Interpretation": "Shani directly influencing GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "17:30", "Planet": "Neptune (Neptune)", "Aspect": "Conjunction", "Nakshatra": "Hasta", "Impact": "0.0%", "Effect": "Neutral", "Action": "HOLD", "Interpretation": "Neptune directly influencing GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "17:30", "Planet": "Saturn (Shani)", "Aspect": "Conjunction", "Nakshatra": "Hasta", "Impact": "0.0%", "Effect": "Neutral", "Action": "HOLD", "Interpretation": "Shani directly influencing GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "17:30", "Planet": "Pluto (Pluto)", "Aspect": "Conjunction", "Nakshatra": "Hasta", "Impact": "0.0%", "Effect": "Neutral", "Action": "HOLD", "Interpretation": "Pluto directly influencing GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "17:30", "Planet": "Neptune (Neptune)", "Aspect": "Conjunction", "Nakshatra": "Hasta", "Impact": "0.0%", "Effect": "Neutral", "Action": "HOLD", "Interpretation": "Neptune directly influencing GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "17:30", "Planet": "Pluto (Pluto)", "Aspect": "Conjunction", "Nakshatra": "Hasta", "Impact": "0.0%", "Effect": "Neutral", "Action": "HOLD", "Interpretation": "Pluto directly influencing GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "18:00", "Planet": "Sun (Surya)", "Aspect": "Trine", "Nakshatra": "Krittika", "Impact": "+0.6%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Surya for GOLD (Nakshatra: Krittika)"},
    {"Date": "2025-07-29", "Time": "18:00", "Planet": "Moon (Chandra)", "Aspect": "Conjunction", "Nakshatra": "Rohini", "Impact": "+0.5%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Chandra directly influencing GOLD (Nakshatra: Rohini)"},
    {"Date": "2025-07-29", "Time": "19:00", "Planet": "Mercury (Budha)", "Aspect": "Sextile", "Nakshatra": "Hasta", "Impact": "+0.4%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Favorable energy from Budha for GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "19:00", "Planet": "Venus (Shukra)", "Aspect": "Square", "Nakshatra": "Uttara Phalguni", "Impact": "-0.3%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Challenging aspect from Shukra on GOLD (Nakshatra: Uttara Phalguni)"},
    {"Date": "2025-07-29", "Time": "20:00", "Planet": "Mars (Mangala)", "Aspect": "Trine", "Nakshatra": "Mrigashira", "Impact": "+0.3%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Mangala for GOLD (Nakshatra: Mrigashira)"},
    {"Date": "2025-07-29", "Time": "20:00", "Planet": "Jupiter (Guru)", "Aspect": "Opposition", "Nakshatra": "Punarvasu", "Impact": "-0.4%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Polarized influence from Guru on GOLD (Nakshatra: Punarvasu)"},
    {"Date": "2025-07-29", "Time": "21:00", "Planet": "Saturn (Shani)", "Aspect": "Trine", "Nakshatra": "Hasta", "Impact": "+0.2%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Shani for GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "21:00", "Planet": "Uranus (Uranus)", "Aspect": "Sextile", "Nakshatra": "Hasta", "Impact": "+0.1%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Favorable energy from Uranus for GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "22:00", "Planet": "Neptune (Neptune)", "Aspect": "Conjunction", "Nakshatra": "Hasta", "Impact": "0.0%", "Effect": "Neutral", "Action": "HOLD", "Interpretation": "Neptune directly influencing GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "22:00", "Planet": "Pluto (Pluto)", "Aspect": "Trine", "Nakshatra": "Hasta", "Impact": "+0.3%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Harmonious support from Pluto for GOLD (Nakshatra: Hasta)"},
    {"Date": "2025-07-29", "Time": "23:00", "Planet": "Sun (Surya)", "Aspect": "Sextile", "Nakshatra": "Krittika", "Impact": "+0.4%", "Effect": "Mild Bullish", "Action": "BUY", "Interpretation": "Favorable energy from Surya for GOLD (Nakshatra: Krittika)"},
    {"Date": "2025-07-29", "Time": "23:00", "Planet": "Moon (Chandra)", "Aspect": "Square", "Nakshatra": "Rohini", "Impact": "-0.2%", "Effect": "Mild Bearish", "Action": "SELL", "Interpretation": "Challenging aspect from Chandra on GOLD (Nakshatra: Rohini)"},
]

# Convert to DataFrame
df = pd.DataFrame(intraday_transits)

# Apply styling
def color_effect(val):
    colors = {
        "Strong Bullish": "#27ae60",
        "Mild Bullish": "#2ecc71",
        "Neutral": "#95a5a6",
        "Mild Bearish": "#e67e22",
        "Strong Bearish": "#e74c3c"
    }
    return f'background-color: {colors.get(val, "#95a5a6")}; color: white'

def color_action(val):
    colors = {
        "STRONG BUY": "#16a085",
        "BUY": "#27ae60",
        "HOLD": "#95a5a6",
        "SELL": "#e67e22",
        "STRONG SELL": "#c0392b"
    }
    return f'background-color: {colors.get(val, "#95a5a6")}; color: white; font-weight: bold'

styled_df = df.style\
    .applymap(color_effect, subset=['Effect'])\
    .applymap(color_action, subset=['Action'])\
    .set_properties(**{'text-align': 'left'})

# Display the report
st.dataframe(
    styled_df,
    column_config={
        "Date": "Date",
        "Time": "Time",
        "Planet": "Planet",
        "Aspect": "Aspect",
        "Nakshatra": "Nakshatra",
        "Impact": "Impact",
        "Effect": "Effect",
        "Action": "Action",
        "Interpretation": "Interpretation"
    },
    use_container_width=True,
    hide_index=True
)
