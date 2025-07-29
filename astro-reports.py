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
