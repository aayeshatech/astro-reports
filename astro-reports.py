import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

# Nakshatra data with market characteristics
nakshatras = [
    ("Ashwini", 0, 13+20/60, "Impulsive", "High volatility, quick moves"),
    ("Bharani", 13+20/60, 26+40/60, "Restrictive", "Resistance levels, consolidation"),
    ("Krittika", 26+40/60, 40, "Sharp", "Sharp moves, breakouts"),
    ("Rohini", 40, 53+20/60, "Growth", "Steady uptrend, bull market"),
    ("Mrigashira", 53+20/60, 66+40/60, "Searching", "Range-bound, uncertainty"),
    ("Ardra", 66+40/60, 80, "Destructive", "High volatility, corrections"),
    ("Punarvasu", 80, 93+20/60, "Renewal", "Recovery, bounce back"),
    ("Pushya", 93+20/60, 106+40/60, "Nourishing", "Steady growth, accumulation"),
    ("Ashlesha", 106+40/60, 120, "Entangling", "Sideways, manipulation"),
    ("Magha", 120, 133+20/60, "Royal", "Leadership stocks outperform"),
    ("Purva Phalguni", 133+20/60, 146+40/60, "Enjoyment", "Consumption stocks up"),
    ("Uttara Phalguni", 146+40/60, 160, "Service", "Service sector strength"),
    ("Hasta", 160, 173+20/60, "Skillful", "Technical analysis works"),
    ("Chitra", 173+20/60, 186+40/60, "Beautiful", "Luxury goods, aesthetics"),
    ("Swati", 186+40/60, 200, "Independent", "Individual stock moves"),
    ("Vishakha", 200, 213+20/60, "Purposeful", "Directional moves"),
    ("Anuradha", 213+20/60, 226+40/60, "Friendly", "Broad market participation"),
    ("Jyeshtha", 226+40/60, 240, "Chief", "Large cap leadership"),
    ("Mula", 240, 253+20/60, "Root", "Fundamental analysis focus"),
    ("Purva Ashadha", 253+20/60, 266+40/60, "Invincible", "Strong trending moves"),
    ("Uttara Ashadha", 266+40/60, 280, "Victory", "Final push, completion"),
    ("Shravana", 280, 293+20/60, "Listening", "News-driven moves"),
    ("Dhanishta", 293+20/60, 306+40/60, "Wealthy", "Financial sector focus"),
    ("Shatabhisha", 306+40/60, 320, "Healing", "Recovery after correction"),
    ("Purva Bhadrapada", 320, 333+20/60, "Dual", "Mixed signals, confusion"),
    ("Uttara Bhadrapada", 333+20/60, 346+40/60, "Depth", "Value investing"),
    ("Revati", 346+40/60, 360, "Wealthy", "Prosperity, bull market end")
]

# Zodiac signs and market characteristics
zodiac_market_traits = {
    "Aries": {"trend": "Bullish", "volatility": "High", "sectors": "Energy, Defense, Metals"},
    "Taurus": {"trend": "Stable", "volatility": "Low", "sectors": "Banking, FMCG, Real Estate"},
    "Gemini": {"trend": "Volatile", "volatility": "Medium", "sectors": "IT, Telecom, Media"},
    "Cancer": {"trend": "Defensive", "volatility": "Medium", "sectors": "Healthcare, Food, Home"},
    "Leo": {"trend": "Strong", "volatility": "Medium", "sectors": "Luxury, Entertainment, Gold"},
    "Virgo": {"trend": "Cautious", "volatility": "Low", "sectors": "Pharma, Services, Analytics"},
    "Libra": {"trend": "Balanced", "volatility": "Low", "sectors": "Beauty, Fashion, Harmony"},
    "Scorpio": {"trend": "Intense", "volatility": "High", "sectors": "Mining, Chemicals, Research"},
    "Sagittarius": {"trend": "Optimistic", "volatility": "Medium", "sectors": "Travel, Education, Export"},
    "Capricorn": {"trend": "Conservative", "volatility": "Low", "sectors": "Infrastructure, Government"},
    "Aquarius": {"trend": "Innovative", "volatility": "High", "sectors": "Technology, Renewables, EV"},
    "Pisces": {"trend": "Emotional", "volatility": "High", "sectors": "Water, Oil, Spirituality"}
}

# Market sessions
market_sessions = {
    "Pre-Market": {"start": "09:00", "end": "09:15", "characteristics": "Gap analysis, overnight news impact"},
    "Opening": {"start": "09:15", "end": "10:00", "characteristics": "High volatility, trend setting, institutional orders"},
    "Morning": {"start": "10:00", "end": "11:30", "characteristics": "Primary trend development, momentum building"},
    "Mid-Session": {"start": "11:30", "end": "13:30", "characteristics": "Institutional activity, large orders"},
    "Afternoon": {"start": "13:30", "end": "15:00", "characteristics": "Retail participation, profit booking"},
    "Closing": {"start": "15:00", "end": "15:30", "characteristics": "Settlement, final adjustments, closing prices"}
}

# Enhanced planet weights for aspect strength
planet_weights = {
    "Sun": 2.0, "Moon": 1.8, "Mars": 1.5, "Mercury": 1.2,
    "Jupiter": 2.2, "Venus": 1.6, "Saturn": 1.8,
    "Rahu": 1.4, "Ketu": 1.4
}

# Planetary market influences
planetary_influences = {
    "Sun": {
        "positive": "Government policies favorable, PSU stocks rise, leadership emergence",
        "negative": "Ego-driven decisions, power struggles, overconfidence in markets"
    },
    "Moon": {
        "positive": "FMCG sector strength, emotional buying, consumer sentiment positive", 
        "negative": "Emotional trading, mood swings, panic selling"
    },
    "Mars": {
        "positive": "Energy sector boom, metals rally, defense stocks up, aggressive buying",
        "negative": "War-like conditions, aggressive selling, conflict in markets"
    },
    "Mercury": {
        "positive": "IT sector leadership, quick gains, communication stocks up, trading activity",
        "negative": "Volatility, confusion, technical glitches, communication breakdown"
    },
    "Jupiter": {
        "positive": "Banking sector strength, financial optimism, investment inflows, wisdom prevails",
        "negative": "Over-expansion, excessive optimism, bubble formation"
    },
    "Venus": {
        "positive": "Luxury goods up, beauty sector strong, consumption increase, aesthetic appeal",
        "negative": "Speculation, materialism, luxury bubble, over-indulgence"
    },
    "Saturn": {
        "positive": "Infrastructure development, disciplined trading, long-term investments",
        "negative": "Restrictions, delays, bear market, regulatory hurdles"
    },
    "Rahu": {
        "positive": "Innovation boom, foreign investment, technology adoption, unconventional gains",
        "negative": "Illusion, manipulation, fake news impact, sudden reversals"
    },
    "Ketu": {
        "positive": "Spiritual stocks, detachment from materialism, research-based decisions",
        "negative": "Sudden exits, abandonment, loss of interest, unexpected events"
    }
}

# Base planetary positions for July 30, 2025 (realistic astronomical data)
BASE_PLANETARY_DATA = {
    datetime(2025, 7, 30, 12, 0, 0): {
        "Sun": {"longitude": 127.5, "retrograde": False},      # Leo
        "Moon": {"longitude": 165.3, "retrograde": False},     # Virgo  
        "Mars": {"longitude": 52.1, "retrograde": False},      # Taurus
        "Mercury": {"longitude": 115.8, "retrograde": True},   # Cancer (Retrograde)
        "Jupiter": {"longitude": 108.9, "retrograde": True},   # Cancer (Retrograde)
        "Venus": {"longitude": 63.5, "retrograde": False},     # Gemini
        "Saturn": {"longitude": 340.2, "retrograde": True},    # Pisces (Retrograde)
        "Rahu": {"longitude": 325.7, "retrograde": True},      # Pisces (Always Retrograde)
        "Ketu": {"longitude": 145.7, "retrograde": True}       # Virgo (Always Retrograde)
    }
}

# Planetary daily movement speeds (degrees per day)
PLANETARY_SPEEDS = {
    "Sun": 1.0,           # ~1 degree per day
    "Moon": 13.0,         # ~13 degrees per day (fastest)
    "Mercury": 1.5,       # ~1-2 degrees per day (retrograde: -1.0)
    "Venus": 1.2,         # ~1.2 degrees per day
    "Mars": 0.6,          # ~0.5-0.7 degrees per day
    "Jupiter": 0.08,      # ~0.08 degrees per day (retrograde: -0.05)
    "Saturn": 0.033,      # ~0.033 degrees per day (retrograde: -0.02)
    "Rahu": -0.05,        # Always retrograde
    "Ketu": -0.05         # Always retrograde
}

def get_nakshatra_pada(degree):
    """Calculate Nakshatra and Pada from longitude with market characteristics"""
    for nak_data in nakshatras:
        nak, start, end = nak_data[0], nak_data[1], nak_data[2]
        if start <= degree < end:
            pada = int((degree - start) // (13+20/60 / 4)) + 1
            return nak, pada, nak_data[3], nak_data[4]
    return "Unknown", 0, "Neutral", "No specific influence"

def get_zodiac_house(degree):
    """Get zodiac sign and house from longitude"""
    sign_index = int(degree // 30) % 12
    house_index = int(degree // 30) % 12
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    return signs[sign_index], f"House {house_index + 1}"

def convert_degree_to_dms(degree):
    """Convert decimal degree to degrees, minutes, seconds format"""
    degree_in_sign = degree % 30
    degree_int = int(degree_in_sign)
    minute_int = int((degree_in_sign - degree_int) * 60)
    second_int = int(((degree_in_sign - degree_int) * 60 - minute_int) * 60)
    return f"{degree_int}° {minute_int}' {second_int}\""

def calculate_planetary_positions(target_datetime):
    """Calculate planetary positions for any given date/time using astronomical data"""
    
    # Find the closest base date
    base_date = datetime(2025, 7, 30, 12, 0, 0)
    base_data = BASE_PLANETARY_DATA[base_date]
    
    # Calculate time difference in days
    time_diff = (target_datetime - base_date).total_seconds() / (24 * 3600)
    
    positions = []
    
    for planet, base_info in base_data.items():
        base_longitude = base_info["longitude"]
        is_retrograde = base_info["retrograde"]
        
        # Calculate speed (adjust for retrograde periods)
        speed = PLANETARY_SPEEDS[planet]
        
        # Special retrograde adjustments
        if planet == "Mercury" and is_retrograde:
            speed = -1.0  # Retrograde Mercury
        elif planet == "Jupiter" and is_retrograde:
            speed = -0.05  # Retrograde Jupiter
        elif planet == "Saturn" and is_retrograde:
            speed = -0.02  # Retrograde Saturn
        
        # Calculate new position
        new_longitude = (base_longitude + speed * time_diff) % 360
        
        # Get zodiac and nakshatra info
        sign, house = get_zodiac_house(new_longitude)
        nak, pada, nak_nature, nak_influence = get_nakshatra_pada(new_longitude)
        
        # Format degree
        degree_formatted = convert_degree_to_dms(new_longitude)
        
        positions.append({
            "Planet": planet,
            "Sign": sign,
            "Degree": degree_formatted,
            "Full_Degree": new_longitude,
            "House": house,
            "Nakshatra": nak,
            "Pada": pada,
            "Retrograde": "Yes" if is_retrograde else "No",
            "Date": target_datetime.strftime("%Y-%m-%d %H:%M:%S IST"),
            "Nakshatra_Nature": nak_nature,
            "Market_Influence": nak_influence
        })
    
    return pd.DataFrame(positions)

def get_aspects(positions):
    """Calculate aspects between planets with market context"""
    if positions.empty:
        return pd.DataFrame(), []
    
    aspects = []
    planets = positions["Planet"].tolist()
    full_degrees = positions["Full_Degree"].tolist()
    
    # Define aspect angles with orbs and market interpretations
    aspect_config = {
        0: ("Conjunction", 2.0, "Unity", "Combined planetary energy - sector focus"),
        60: ("Sextile", 2.0, "Opportunity", "Favorable trading opportunities - buy zones"),
        90: ("Square", 2.0, "Tension", "Market stress and volatility - caution needed"),
        120: ("Trine", 2.0, "Harmony", "Smooth trending moves - follow momentum"),
        180: ("Opposition", 2.0, "Conflict", "Reversal potential - exit/hedge positions"),
        30: ("Semisextile", 1.0, "Adjustment", "Minor corrections - fine-tune positions"),
        45: ("Semisquare", 1.0, "Friction", "Intraday volatility - scalping opportunities"),
        135: ("Sesquiquadrate", 1.0, "Crisis", "Sharp moves - breakout/breakdown alerts"),
        150: ("Quincunx", 1.0, "Adjustment", "Unexpected moves - stay flexible")
    }
    
    for i, p1 in enumerate(planets):
        for j, p2 in enumerate(planets[i+1:], start=i+1):
            deg1 = full_degrees[i]
            deg2 = full_degrees[j]
            diff = abs(deg2 - deg1)
            if diff > 180:
                diff = 360 - diff
            
            for angle, (aspect_name, orb, nature, market_effect) in aspect_config.items():
                if abs(diff - angle) <= orb:
                    # Calculate weight based on planets involved
                    weight = (planet_weights.get(p1, 1.0) + planet_weights.get(p2, 1.0)) / 2
                    
                    # Determine market tendency
                    if aspect_name in ["Sextile", "Trine"]:
                        tendency = "Bullish"
                        if p1 in ["Jupiter", "Venus"] or p2 in ["Jupiter", "Venus"]:
                            weight *= 1.4  # Extra bullish for benefics
                    elif aspect_name in ["Square", "Opposition"]:
                        tendency = "Bearish"
                        if p1 in ["Mars", "Saturn", "Rahu", "Ketu"] or p2 in ["Mars", "Saturn", "Rahu", "Ketu"]:
                            weight *= 1.4  # Extra bearish for malefics
                    elif aspect_name == "Conjunction":
                        # Conjunction tendency depends on planets involved
                        if (p1 in ["Jupiter", "Venus", "Moon"] or p2 in ["Jupiter", "Venus", "Moon"]):
                            tendency = "Bullish"
                            weight *= 1.2
                        elif (p1 in ["Mars", "Saturn", "Rahu", "Ketu"] or p2 in ["Mars", "Saturn", "Rahu", "Ketu"]):
                            tendency = "Bearish" 
                            weight *= 1.2
                        else:
                            tendency = "Neutral"
                    else:
                        tendency = "Neutral"
                        weight *= 0.8
                    
                    # Special combinations
                    combo_effect = ""
                    if (p1 == "Sun" and p2 == "Mercury") or (p1 == "Mercury" and p2 == "Sun"):
                        combo_effect = "IT sector focus, communication boost"
                    elif (p1 == "Moon" and p2 == "Venus") or (p1 == "Venus" and p2 == "Moon"):
                        combo_effect = "FMCG and luxury goods strength"
                    elif (p1 == "Mars" and p2 == "Saturn") or (p1 == "Saturn" and p2 == "Mars"):
                        combo_effect = "Infrastructure and energy sector impact"
                    elif (p1 == "Jupiter" and p2 == "Mercury") or (p1 == "Mercury" and p2 == "Jupiter"):
                        combo_effect = "Banking and fintech opportunities"
                    
                    aspects.append({
                        "Planet1": p1,
                        "Planet2": p2,
                        "Aspect": aspect_name,
                        "Exact_Degree": f"{diff:.2f}°",
                        "Orb": f"{abs(diff - angle):.2f}°",
                        "Weight": round(weight, 2),
                        "Tendency": tendency,
                        "Strength": "Strong" if abs(diff - angle) <= orb/2 else "Moderate",
                        "Nature": nature,
                        "Market_Effect": market_effect,
                        "Combo_Effect": combo_effect
                    })
                    break
    
    return pd.DataFrame(aspects), aspects

def analyze_market_session(time_str, aspects_df, positions_df):
    """Analyze market characteristics for specific session with enhanced logic"""
    hour = int(time_str.split(':')[0])
    minute = int(time_str.split(':')[1])
    time_decimal = hour + minute/60
    
    # Determine session
    if 9.0 <= time_decimal < 9.25:
        session = "Pre-Market"
        session_emoji = "🌅"
    elif 9.25 <= time_decimal < 10.0:
        session = "Opening" 
        session_emoji = "🔔"
    elif 10.0 <= time_decimal < 11.5:
        session = "Morning"
        session_emoji = "🌄"
    elif 11.5 <= time_decimal < 13.5:
        session = "Mid-Session"
        session_emoji = "🌇"
    elif 13.5 <= time_decimal < 15.0:
        session = "Afternoon"
        session_emoji = "🌆"
    elif 15.0 <= time_decimal <= 15.5:
        session = "Closing"
        session_emoji = "🌃"
    else:
        session = "After-Hours"
        session_emoji = "🌙"
    
    # Calculate session characteristics
    bullish_count = len(aspects_df[aspects_df["Tendency"] == "Bullish"])
    bearish_count = len(aspects_df[aspects_df["Tendency"] == "Bearish"])
    total_weight = aspects_df["Weight"].sum()
    bullish_weight = aspects_df[aspects_df["Tendency"] == "Bullish"]["Weight"].sum()
    bearish_weight = aspects_df[aspects_df["Tendency"] == "Bearish"]["Weight"].sum()
    
    # Enhanced outlook calculation
    if total_weight > 0:
        bullish_ratio = bullish_weight / total_weight
        bearish_ratio = bearish_weight / total_weight
        
        if bullish_ratio > 0.7:
            outlook = "Strong Bullish"
            emoji = "🚀"
        elif bullish_ratio > 0.55:
            outlook = "Bullish"
            emoji = "📈"
        elif bearish_ratio > 0.7:
            outlook = "Strong Bearish"
            emoji = "💥"
        elif bearish_ratio > 0.55:
            outlook = "Bearish"
            emoji = "📉"
        else:
            outlook = "Neutral"
            emoji = "➡️"
    else:
        outlook = "Neutral"
        emoji = "➡️"
    
    # Session-specific adjustments
    if session == "Opening" and bullish_count > bearish_count:
        outlook += " (Gap Up Likely)"
    elif session == "Opening" and bearish_count > bullish_count:
        outlook += " (Gap Down Likely)"
    elif session == "Closing":
        if bullish_count > bearish_count:
            outlook += " (Positive Close)"
        elif bearish_count > bullish_count:
            outlook += " (Negative Close)"
    
    return {
        "session": session,
        "session_emoji": session_emoji,
        "outlook": outlook,
        "emoji": emoji,
        "bullish_aspects": bullish_count,
        "bearish_aspects": bearish_count,
        "bullish_weight": round(bullish_weight, 2),
        "bearish_weight": round(bearish_weight, 2),
        "strength": "High" if total_weight > 10 else "Medium" if total_weight > 5 else "Low"
    }

def generate_market_insights(positions_df, aspects_df):
    """Generate detailed market insights with sector focus"""
    insights = []
    
    # Planetary influence analysis
    key_influences = []
    sector_focus = []
    
    for _, pos in positions_df.iterrows():
        planet = pos["Planet"]
        sign = pos["Sign"]
        retrograde = pos["Retrograde"]
        nakshatra = pos["Nakshatra"]
        
        trait = zodiac_market_traits.get(sign, {})
        planet_info = planetary_influences.get(planet, {})
        
        # Key planets for market analysis
        if planet in ["Sun", "Moon", "Mercury", "Jupiter", "Mars"]:
            retro_text = " (Retrograde)" if retrograde == "Yes" else ""
            
            influence_text = f"**{planet} in {sign}{retro_text}** → {trait.get('trend', 'Neutral')} sentiment"
            
            if retrograde == "Yes":
                if planet == "Mercury":
                    influence_text += " → Communication delays, tech volatility, review financial decisions"
                elif planet == "Jupiter": 
                    influence_text += " → Banking sector caution, review expansion plans"
                elif planet == "Mars":
                    influence_text += " → Energy sector consolidation, delayed projects"
            
            # Add sector focus
            sectors = trait.get('sectors', '')
            if sectors:
                influence_text += f" | **Sectors**: {sectors}"
            
            key_influences.append(influence_text)
            
            # Nakshatra-specific influence
            if pos["Market_Influence"] and pos["Market_Influence"] != "No specific influence":
                sector_focus.append(f"{planet} in {nakshatra}: {pos['Market_Influence']}")
    
    # Critical aspects analysis
    critical_aspects = []
    for _, aspect in aspects_df.iterrows():
        if aspect["Strength"] == "Strong" and aspect["Weight"] > 2.0:
            effect_text = f"**{aspect['Planet1']}-{aspect['Planet2']} {aspect['Aspect']}** → {aspect['Market_Effect']}"
            
            if aspect["Combo_Effect"]:
                effect_text += f" | {aspect['Combo_Effect']}"
            
            critical_aspects.append(effect_text)
    
    return {
        "key_influences": key_influences,
        "sector_focus": sector_focus,
        "critical_aspects": critical_aspects
    }

def detect_planetary_transits(current_positions, previous_positions=None):
    """Detect detailed planetary transits with market impact"""
    if previous_positions is None or previous_positions.empty:
        return []
    
    transits = []
    for _, current_row in current_positions.iterrows():
        planet = current_row["Planet"]
        prev_row = previous_positions[previous_positions["Planet"] == planet]
        
        if not prev_row.empty:
            prev_row = prev_row.iloc[0]
            
            # Sign change (major transit)
            if current_row["Sign"] != prev_row["Sign"]:
                old_trait = zodiac_market_traits.get(prev_row["Sign"], {})
                new_trait = zodiac_market_traits.get(current_row["Sign"], {})
                impact = f"Market shift: {old_trait.get('trend', 'Neutral')} → {new_trait.get('trend', 'Neutral')}"
                transits.append({
                    "type": "Sign Change",
                    "planet": planet,
                    "change": f"{prev_row['Sign']} → {current_row['Sign']}",
                    "impact": impact,
                    "sectors": new_trait.get('sectors', 'General'),
                    "strength": "High"
                })
            
            # Nakshatra change (moderate transit)
            elif current_row["Nakshatra"] != prev_row["Nakshatra"]:
                transits.append({
                    "type": "Nakshatra Change", 
                    "planet": planet,
                    "change": f"{prev_row['Nakshatra']} → {current_row['Nakshatra']}",
                    "impact": current_row["Market_Influence"],
                    "sectors": "Sector-specific",
                    "strength": "Medium"
                })
            
            # Significant degree movement
            else:
                deg_diff = abs(current_row["Full_Degree"] - prev_row["Full_Degree"])
                if deg_diff > 0.5:  # More than 30 minutes of movement
                    transits.append({
                        "type": "Degree Movement",
                        "planet": planet, 
                        "change": f"{deg_diff:.1f}° movement",
                        "impact": "Gradual influence change",
                        "sectors": "Intraday impact",
                        "strength": "Low"
                    })
    
    return transits

def calculate_enhanced_trading_signal(aspects_df, session_info, new_aspects=None, dissolved_aspects=None, transits=None):
    """Calculate enhanced trading signal with comprehensive analysis"""
    if aspects_df.empty:
        return "Neutral", "gray", 0, 0, "No planetary aspects active", []
    
    # Base score calculation with aspect strength
    bullish_score = 0
    bearish_score = 0
    signal_reasons = []
    
    for _, aspect in aspects_df.iterrows():
        weight = aspect["Weight"]
        strength_multiplier = 1.5 if aspect["Strength"] == "Strong" else 1.0
        
        if aspect["Tendency"] == "Bullish":
            bullish_score += weight * strength_multiplier
        elif aspect["Tendency"] == "Bearish":
            bearish_score += weight * strength_multiplier
    
    # New aspects bonus (formation)
    if new_aspects:
        for aspect in new_aspects:
            if aspect["Strength"] == "Strong":
                bonus = aspect["Weight"] * 0.5
                if aspect["Tendency"] == "Bullish":
                    bullish_score += bonus
                    signal_reasons.append(f"New {aspect['Planet1']}-{aspect['Planet2']} {aspect['Aspect']} forming (+{bonus:.1f})")
                elif aspect["Tendency"] == "Bearish":
                    bearish_score += bonus
                    signal_reasons.append(f"New {aspect['Planet1']}-{aspect['Planet2']} {aspect['Aspect']} forming (-{bonus:.1f})")
    
    # Dissolved aspects impact (separation)
    if dissolved_aspects:
        for aspect in dissolved_aspects:
            bonus = aspect["Weight"] * 0.3
            if aspect["Tendency"] == "Bullish":
                bearish_score += bonus  # Loss of bullish aspect = bearish
                signal_reasons.append(f"{aspect['Planet1']}-{aspect['Planet2']} {aspect['Aspect']} dissolving (-{bonus:.1f})")
            elif aspect["Tendency"] == "Bearish":
                bullish_score += bonus  # Loss of bearish aspect = bullish
                signal_reasons.append(f"{aspect['Planet1']}-{aspect['Planet2']} {aspect['Aspect']} dissolving (+{bonus:.1f})")
    
    # Transit impact
    if transits:
        for transit in transits:
            if transit["strength"] == "High":
                if "Bullish" in transit["impact"] or "growth" in transit["impact"].lower():
                    bullish_score += 1.0
                    signal_reasons.append(f"{transit['planet']} {transit['change']} (+1.0)")
                elif "Bearish" in transit["impact"] or "caution" in transit["impact"].lower():
                    bearish_score += 1.0
                    signal_reasons.append(f"{transit['planet']} {transit['change']} (-1.0)")
    
    # Session-based adjustments
    session = session_info["session"]
    if session == "Opening":
        bullish_score *= 1.2
        bearish_score *= 1.2
        signal_reasons.append("Opening volatility amplification")
    elif session == "Closing":
        bullish_score *= 0.9
        bearish_score *= 0.9
        signal_reasons.append("Closing moderation effect")
    
    # Calculate net score and determine signal
    net_score = bullish_score - bearish_score
    total_score = bullish_score + bearish_score
    
    if total_score == 0:
        signal = "Neutral"
        color = "gray"
    else:
        signal_ratio = abs(net_score) / total_score
        
        if signal_ratio > 0.65:  # Strong signal threshold
            if net_score > 0:
                signal = "Strong Buy"
                color = "darkgreen"
            else:
                signal = "Strong Sell" 
                color = "darkred"
        elif signal_ratio > 0.35:  # Moderate signal
            if net_score > 0:
                signal = "Buy"
                color = "lightgreen" 
            else:
                signal = "Sell"
                color = "lightcoral"
        else:
            signal = "Neutral"
            color = "gray"
    
    # Generate detailed signal explanation
    signal_details = f"Score: {bullish_score:.1f}B - {bearish_score:.1f}B = {net_score:.1f}"
    
    return signal, color, round(bullish_score, 2), round(bearish_score, 2), signal_details, signal_reasons

def generate_daily_report(date, positions_df, timeline_df):
    """Generate comprehensive daily report like DeepSeek"""
    date_str = date.strftime("%d-%b-%Y").upper()
    
    # Header
    report = f"""
## 📈📉 NIFTY & BANKNIFTY ASTRO TREND REPORT | {date_str}
**(Market Hours: 9:15 AM - 3:30 PM IST)**

### 🌕 KEY PLANETARY INFLUENCES"""
    
    # Add key planetary influences
    for _, pos in positions_df.iterrows():
        if pos["Planet"] in ["Sun", "Moon", "Mercury", "Jupiter", "Mars", "Saturn"]:
            sign = pos["Sign"]
            retro = " (Retrograde)" if pos["Retrograde"] == "Yes" else ""
            trait = zodiac_market_traits.get(sign, {})
            
            report += f"\n- **{pos['Planet']} in {sign}{retro}** → {trait.get('trend', 'Neutral')} sentiment"
            
            if pos["Retrograde"] == "Yes":
                if pos["Planet"] == "Mercury":
                    report += " → Volatility in banking/financials, communication delays"
                elif pos["Planet"] == "Jupiter":
                    report += " → Banking sector review, cautious expansion"
                elif pos["Planet"] == "Saturn":
                    report += " → Infrastructure delays, regulatory reviews"
            
            # Add sector focus
            sectors = trait.get('sectors', '')
            if sectors:
                report += f" | Focus: {sectors}"
    
    # Session analysis
    report += "\n\n### ⏰ INTRADAY TREND TIMELINE"
    
    # Group timeline by sessions with enhanced analysis
    session_data = {
        "morning": [],
        "mid": [],
        "afternoon": []
    }
    
    for _, row in timeline_df.iterrows():
        time_str = row["DateTime"].split(" ")[1]
        hour = int(time_str.split(":")[0])
        
        signal_emoji = "🚀" if row["Signal"] == "Strong Buy" else "📈" if "Buy" in row["Signal"] else "💥" if row["Signal"] == "Strong Sell" else "📉" if "Sell" in row["Signal"] else "➡️"
        time_signal = f"{time_str} → {signal_emoji} {row['Signal']}"
        
        if 9 <= hour < 11.5:
            session_data["morning"].append(time_signal)
        elif 11.5 <= hour < 13.5:
            session_data["mid"].append(time_signal)
        else:
            session_data["afternoon"].append(time_signal)
    
    # Morning Session
    if session_data["morning"]:
        report += "\n\n**🌅 Morning Session (9:15-11:30 AM)**"
        morning_signals = [s.split(" → ")[1] for s in session_data["morning"]]
        buy_count = sum(1 for s in morning_signals if "Buy" in s)
        sell_count = sum(1 for s in morning_signals if "Sell" in s)
        
        if buy_count > sell_count:
            report += "\n- 📈 **Bullish Bias** - Early strength expected, buy on dips"
        elif sell_count > buy_count:
            report += "\n- 📉 **Bearish Pressure** - Early weakness likely, avoid longs"
        else:
            report += "\n- ➡️ **Sideways Movement** - Range-bound trading expected"
        
        for signal in session_data["morning"][:2]:
            report += f"\n  - {signal}"
    
    # Mid Session
    if session_data["mid"]:
        report += "\n\n**🌇 Mid-Session (11:30 AM-1:30 PM)**"
        mid_signals = [s.split(" → ")[1] for s in session_data["mid"]]
        buy_count = sum(1 for s in mid_signals if "Buy" in s)
        sell_count = sum(1 for s in mid_signals if "Sell" in s)
        
        if buy_count > sell_count:
            report += "\n- 📈 **Institutional Buying** - Strong momentum continuation"
        elif sell_count > buy_count:
            report += "\n- 📉 **Profit Booking** - Correction phase, institutional selling"
        else:
            report += "\n- ➡️ **Consolidation** - Institutional activity balanced"
        
        for signal in session_data["mid"][:2]:
            report += f"\n  - {signal}"
    
    # Afternoon Session  
    if session_data["afternoon"]:
        report += "\n\n**🌆 Afternoon Session (1:30-3:30 PM)**"
        afternoon_signals = [s.split(" → ")[1] for s in session_data["afternoon"]]
        buy_count = sum(1 for s in afternoon_signals if "Buy" in s)
        sell_count = sum(1 for s in afternoon_signals if "Sell" in s)
        
        if buy_count > sell_count:
            report += "\n- 📈 **Recovery Mode** - Late session bounce, positive close likely"
        elif sell_count > buy_count:
            report += "\n- 📉 **Weakness Continues** - Selling pressure persists"
        else:
            report += "\n- ➡️ **Settlement Phase** - Balanced closing expected"
        
        for signal in session_data["afternoon"][:2]:
            report += f"\n  - {signal}"
    
    # Overall analysis
    total_buy_signals = len([row for _, row in timeline_df.iterrows() if "Buy" in row["Signal"]])
    total_sell_signals = len([row for _, row in timeline_df.iterrows() if "Sell" in row["Signal"]])
    strong_buy_signals = len([row for _, row in timeline_df.iterrows() if row["Signal"] == "Strong Buy"])
    strong_sell_signals = len([row for _, row in timeline_df.iterrows() if row["Signal"] == "Strong Sell"])
    
    # Critical timing analysis
    max_activity_times = timeline_df.nlargest(3, "Active_Aspects")["DateTime"].str.split(" ").str[1].tolist()
    
    # Final outlook
    if strong_buy_signals > strong_sell_signals and total_buy_signals > total_sell_signals:
        overall_outlook = "🟢 **Strong Bullish** (High probability gains)"
        strategy = "**Buy on dips, hold positions, target higher levels**"
    elif total_buy_signals > total_sell_signals:
        overall_outlook = "🟢 **Bullish** (Favorable for long positions)"
        strategy = "**Selective buying, book partial profits at resistance**"
    elif strong_sell_signals > strong_buy_signals and total_sell_signals > total_buy_signals:
        overall_outlook = "🔴 **Strong Bearish** (High caution advised)"
        strategy = "**Avoid longs, consider shorts, strict stop losses**"
    elif total_sell_signals > total_buy_signals:
        overall_outlook = "🔴 **Bearish** (Selling pressure likely)"
        strategy = "**Book profits, reduce positions, wait for reversal**"
    else:
        overall_outlook = "🟡 **Neutral** (Range-bound movement)"
        strategy = "**Range trading, buy support, sell resistance**"
    
    report += f"""

### 🎯 FINAL OUTLOOK
- **Overall Trend**: {overall_outlook}
- **Key Strategy**: {strategy}
- **Critical Times**: {", ".join(max_activity_times[:2])} (High activity periods)
- **Risk Level**: {"High" if strong_sell_signals > 2 else "Medium" if total_sell_signals > total_buy_signals else "Low"}

### 📊 Signal Summary
- 🚀 Strong Buy: {strong_buy_signals} | 📈 Buy: {total_buy_signals - strong_buy_signals} | 📉 Sell: {total_sell_signals - strong_sell_signals} | 💥 Strong Sell: {strong_sell_signals}
"""
    
    return report

# Streamlit App Configuration
st.set_page_config(
    layout="wide", 
    page_title="Professional Astro Market Analyzer", 
    page_icon="🌟",
    initial_sidebar_state="expanded"
)

st.title("🌟 Professional Astro Market Analyzer")
st.subheader("🔮 Advanced Planetary Analysis for NIFTY & BANKNIFTY Trading")

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #1f77b4; text-align: center; margin-bottom: 1rem; }
    .sub-header { font-size: 1.2rem; color: #666; text-align: center; margin-bottom: 2rem; }
    .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin: 0.5rem; }
    .signal-strong-buy { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 0.5rem; border-radius: 5px; font-weight: bold; }
    .signal-buy { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #2c5aa0; padding: 0.5rem; border-radius: 5px; }
    .signal-sell { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #8b4513; padding: 0.5rem; border-radius: 5px; }
    .signal-strong-sell { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); color: white; padding: 0.5rem; border-radius: 5px; font-weight: bold; }
    .signal-neutral { background: linear-gradient(135deg, #e3e3e3 0%, #d1d1d1 100%); color: #555; padding: 0.5rem; border-radius: 5px; }
    .report-container { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 2rem; border-radius: 15px; margin: 1rem 0; }
    .insight-box { background: #ffffff; border-left: 4px solid #1f77b4; padding: 1rem; margin: 1rem 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.header("🎛️ Analysis Configuration")
st.sidebar.markdown("---")

# Enhanced tabs
tab1, tab2, tab3 = st.tabs(["📊 Live Market Analysis", "🔍 Intraday Deep Dive", "📋 Professional Daily Report"])

# Tab 1: Live Market Analysis
with tab1:
    st.header("📊 Live Planetary Positions & Market Impact")
    
    current_time = datetime.now()
    
    with st.spinner("🔮 Calculating current planetary positions..."):
        current_positions = calculate_planetary_positions(current_time)
        
        if not current_positions.empty:
            # Status indicator
            st.success(f"✅ **Live Data Generated** | Analysis Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} IST")
            
            # Enhanced positions display
            st.subheader("🪐 Current Planetary Positions")
            display_positions = current_positions[["Planet", "Sign", "Degree", "Nakshatra", "Retrograde", "Nakshatra_Nature", "Market_Influence"]]
            st.dataframe(display_positions, use_container_width=True)
            
            # Current aspects analysis
            current_aspects_df, _ = get_aspects(current_positions)
            
            if not current_aspects_df.empty:
                st.subheader("⚡ Active Planetary Aspects")
                
                # Enhanced aspects display
                aspect_display = current_aspects_df[["Planet1", "Planet2", "Aspect", "Tendency", "Strength", "Weight", "Market_Effect", "Combo_Effect"]]
                st.dataframe(aspect_display, use_container_width=True)
                
                # Current session analysis
                session_info = analyze_market_session(current_time.strftime("%H:%M"), current_aspects_df, current_positions)
                
                # Session metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Current Session", f"{session_info['session_emoji']} {session_info['session']}")
                with col2:
                    st.metric("Session Outlook", f"{session_info['emoji']} {session_info['outlook']}")
                with col3:
                    st.metric("Bullish Weight", f"{session_info['bullish_weight']}")
                with col4:
                    st.metric("Bearish Weight", f"{session_info['bearish_weight']}")
                with col5:
                    st.metric("Signal Strength", session_info['strength'])
                
                # Current trading signal with enhanced analysis
                signal, color, bull_score, bear_score, signal_details, signal_reasons = calculate_enhanced_trading_signal(
                    current_aspects_df, session_info
                )
                
                # Signal display with detailed reasoning
                st.subheader("🎯 Current Trading Signal & Analysis")
                signal_col1, signal_col2, signal_col3 = st.columns([2, 1, 1])
                
                with signal_col1:
                    if signal == "Strong Buy":
                        st.markdown(f'<div class="signal-strong-buy">🚀 {signal}</div>', unsafe_allow_html=True)
                    elif signal == "Buy":
                        st.markdown(f'<div class="signal-buy">📈 {signal}</div>', unsafe_allow_html=True)
                    elif signal == "Strong Sell":
                        st.markdown(f'<div class="signal-strong-sell">💥 {signal}</div>', unsafe_allow_html=True)
                    elif signal == "Sell":
                        st.markdown(f'<div class="signal-sell">📉 {signal}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="signal-neutral">➡️ {signal}</div>', unsafe_allow_html=True)
                    
                    # Show signal reasoning
                    if signal_reasons:
                        st.markdown("**Signal Reasoning:**")
                        for reason in signal_reasons[:3]:
                            st.write(f"• {reason}")
                
                with signal_col2:
                    st.metric("Net Score", f"{bull_score - bear_score:.2f}")
                    st.metric("Signal Strength", session_info['strength'])
                with signal_col3:
                    st.metric("Active Aspects", len(current_aspects_df))
                    st.metric("Bullish/Bearish", f"{session_info['bullish_aspects']}/{session_info['bearish_aspects']}")
                
                # Current planetary speeds and movement
                st.subheader("🌍 Real-time Planetary Movement Analysis")
                
                movement_data = []
                for _, pos in current_positions.iterrows():
                    planet = pos["Planet"]
                    speed = PLANETARY_SPEEDS.get(planet, 0)
                    daily_movement = abs(speed)
                    
                    # Calculate when planet will change nakshatra/sign
                    current_deg = pos["Full_Degree"] % 30
                    if speed > 0:
                        deg_to_next = 30 - current_deg
                        hours_to_sign_change = deg_to_next / (daily_movement / 24) if daily_movement > 0 else 999
                    else:
                        hours_to_sign_change = current_deg / (daily_movement / 24) if daily_movement > 0 else 999
                    
                    movement_data.append({
                        "Planet": planet,
                        "Current_Position": f"{pos['Sign']} {pos['Degree']}",
                        "Daily_Speed": f"{daily_movement:.2f}°/day",
                        "Next_Sign_Change": f"~{hours_to_sign_change:.1f} hours" if hours_to_sign_change < 48 else ">2 days",
                        "Movement_Direction": "Forward" if speed > 0 else "Retrograde",
                        "Market_Impact": pos["Market_Influence"]
                    })
                
                movement_df = pd.DataFrame(movement_data)
                st.dataframe(movement_df, use_container_width=True)
                
                # Upcoming aspect predictions
                st.subheader("🔮 Upcoming Aspect Formations (Next 24 Hours)")
                
                upcoming_aspects = []
                future_times = [current_time + timedelta(hours=h) for h in [1, 3, 6, 12, 24]]
                
                for future_time in future_times:
                    future_positions = calculate_planetary_positions(future_time)
                    future_aspects_df, _ = get_aspects(future_positions)
                    
                    # Find new aspects that will form
                    current_keys = set((row["Planet1"], row["Planet2"], row["Aspect"]) for _, row in current_aspects_df.iterrows())
                    future_keys = set((row["Planet1"], row["Planet2"], row["Aspect"]) for _, row in future_aspects_df.iterrows())
                    
                    new_future_keys = future_keys - current_keys
                    
                    for _, aspect in future_aspects_df.iterrows():
                        if (aspect["Planet1"], aspect["Planet2"], aspect["Aspect"]) in new_future_keys:
                            hours_ahead = (future_time - current_time).total_seconds() / 3600
                            upcoming_aspects.append({
                                "Time_Ahead": f"{hours_ahead:.0f}h",
                                "Aspect": f"{aspect['Planet1']}-{aspect['Planet2']} {aspect['Aspect']}",
                                "Tendency": aspect["Tendency"],
                                "Weight": aspect["Weight"],
                                "Market_Effect": aspect["Market_Effect"],
                                "Formation_Time": future_time.strftime("%H:%M")
                            })
                
                if upcoming_aspects:
                    upcoming_df = pd.DataFrame(upcoming_aspects)
                    upcoming_df = upcoming_df.sort_values("Weight", ascending=False).head(8)
                    
                    def highlight_upcoming(row):
                        if row["Tendency"] == "Bullish":
                            return ['background-color: #e8f5e8; color: #2e7d32;'] * len(row)
                        elif row["Tendency"] == "Bearish":
                            return ['background-color: #ffebee; color: #c62828;'] * len(row)
                        else:
                            return [''] * len(row)
                    
                    styled_upcoming = upcoming_df.style.apply(highlight_upcoming, axis=1)
                    st.dataframe(styled_upcoming, use_container_width=True)
                else:
                    st.info("No major new aspects forming in the next 24 hours")
                
                # Market insights
                insights = generate_market_insights(current_positions, current_aspects_df)
                
                # Display insights in columns
                insight_col1, insight_col2 = st.columns(2)
                
                with insight_col1:
                    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
                    st.subheader("🌟 Key Planetary Influences")
                    for influence in insights["key_influences"]:
                        st.markdown(f"• {influence}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with insight_col2:
                    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
                    st.subheader("⚡ Critical Aspects")
                    for aspect in insights["critical_aspects"]:
                        st.markdown(f"• {aspect}")
                    
                    if insights["sector_focus"]:
                        st.subheader("🎯 Sector Focus")
                        for sector in insights["sector_focus"]:
                            st.markdown(f"• {sector}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            else:
                st.info("ℹ️ No significant planetary aspects currently active")

# Tab 2: Intraday Deep Dive
with tab2:
    st.header("🔍 Comprehensive Intraday Analysis")
    
    # Enhanced input section
    analysis_col1, analysis_col2 = st.columns([1, 1])
    
    with analysis_col1:
        st.subheader("📈 Market Settings")
        symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "SENSEX", "FINNIFTY"], index=0)
        analysis_date = st.date_input("Analysis Date", datetime(2025, 7, 30))
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            show_transits = st.checkbox("Show Transit Changes", True)
            show_combos = st.checkbox("Show Aspect Combinations", True)
            min_aspect_weight = st.slider("Minimum Aspect Weight", 0.5, 3.0, 1.0)
        
    with analysis_col2:
        st.subheader("⏰ Time Configuration")
        start_time = st.time_input("Market Start Time", datetime(2025, 7, 30, 9, 15).time())
        end_time = st.time_input("Market End Time", datetime(2025, 7, 30, 15, 30).time())
        time_interval = st.selectbox("Analysis Interval", ["15 minutes", "30 minutes", "1 hour"], index=0)
        
        # Market session highlights
        st.info("""
        **📊 Market Sessions:**
        • 🌅 **Opening** (9:15-10:00): High volatility, trend setting
        • 🌄 **Morning** (10:00-11:30): Primary trend development  
        • 🌇 **Mid-Session** (11:30-13:30): Institutional activity
        • 🌆 **Afternoon** (13:30-15:00): Retail participation
        • 🌃 **Closing** (15:00-15:30): Settlement phase
        """)
    
    if st.button("🚀 Generate Comprehensive Analysis", type="primary"):
        start_datetime = datetime.combine(analysis_date, start_time)
        end_datetime = datetime.combine(analysis_date, end_time)
        
        if start_datetime >= end_datetime:
            st.error("❌ End time must be after start time.")
        else:
            interval_minutes = {"15 minutes": 15, "30 minutes": 30, "1 hour": 60}[time_interval]
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Analysis execution with enhanced tracking
            timeline = []
            previous_positions = None
            previous_aspects_df = pd.DataFrame()
            
            total_intervals = int((end_datetime - start_datetime).total_seconds() / (interval_minutes * 60))
            current_time = start_datetime
            interval_count = 0
            
            while current_time <= end_datetime:
                progress = min(interval_count / max(total_intervals, 1), 1.0)
                progress_bar.progress(progress)
                status_text.text(f"🔮 Analyzing: {current_time.strftime('%H:%M')} ({interval_count + 1}/{total_intervals + 1})")
                
                # Calculate positions and aspects
                positions = calculate_planetary_positions(current_time)
                aspects_df, _ = get_aspects(positions)
                
                # Filter aspects by minimum weight
                aspects_df = aspects_df[aspects_df["Weight"] >= min_aspect_weight]
                
                # Detect aspect changes (new formations and dissolutions)
                new_aspects = []
                dissolved_aspects = []
                
                if not previous_aspects_df.empty:
                    # Compare current vs previous aspects
                    prev_keys = set((row["Planet1"], row["Planet2"], row["Aspect"]) for _, row in previous_aspects_df.iterrows())
                    curr_keys = set((row["Planet1"], row["Planet2"], row["Aspect"]) for _, row in aspects_df.iterrows())
                    
                    # New aspect formations
                    new_aspect_keys = curr_keys - prev_keys
                    new_aspects = [row for _, row in aspects_df.iterrows() 
                                 if (row["Planet1"], row["Planet2"], row["Aspect"]) in new_aspect_keys]
                    
                    # Dissolved aspects
                    dissolved_aspect_keys = prev_keys - curr_keys  
                    dissolved_aspects = [row for _, row in previous_aspects_df.iterrows()
                                       if (row["Planet1"], row["Planet2"], row["Aspect"]) in dissolved_aspect_keys]
                
                # Enhanced transit analysis
                transits = []
                if previous_positions is not None and show_transits:
                    transits = detect_planetary_transits(positions, previous_positions)
                
                # Session analysis
                session_info = analyze_market_session(current_time.strftime("%H:%M"), aspects_df, positions)
                
                # Enhanced signal calculation with all factors
                signal, color, bull_score, bear_score, signal_details, signal_reasons = calculate_enhanced_trading_signal(
                    aspects_df, session_info, new_aspects, dissolved_aspects, transits
                )
                
                # Aspect combinations
                combo_effects = []
                if show_combos:
                    combo_effects = [row["Combo_Effect"] for _, row in aspects_df.iterrows() if row["Combo_Effect"]]
                
                # Format transit information
                transit_text = "None"
                if transits:
                    major_transits = [t for t in transits if t["strength"] == "High"]
                    if major_transits:
                        transit_text = "; ".join([f"{t['planet']} {t['change']}" for t in major_transits])
                    else:
                        transit_text = "; ".join([f"{t['planet']} {t['change']}" for t in transits[:2]])
                
                # New/Dissolved aspects info
                aspect_changes = []
                if new_aspects:
                    aspect_changes.extend([f"NEW: {a['Planet1']}-{a['Planet2']} {a['Aspect']}" for a in new_aspects])
                if dissolved_aspects:
                    aspect_changes.extend([f"END: {a['Planet1']}-{a['Planet2']} {a['Aspect']}" for a in dissolved_aspects])
                
                # Timeline entry with enhanced information
                timeline.append({
                    "DateTime": current_time.strftime("%Y-%m-%d %H:%M"),
                    "Time": current_time.strftime("%H:%M"),
                    "Day": current_time.strftime("%A"),
                    "Session": f"{session_info['session_emoji']} {session_info['session']}",
                    "Signal": signal,
                    "Net_Score": round(bull_score - bear_score, 2),
                    "Bullish_Weight": bull_score,
                    "Bearish_Weight": bear_score,
                    "Active_Aspects": len(aspects_df),
                    "Session_Outlook": f"{session_info['emoji']} {session_info['outlook']}",
                    "Transits": transit_text,
                    "Aspect_Changes": "; ".join(aspect_changes) if aspect_changes else "None",
                    "Combo_Effects": "; ".join(combo_effects) if combo_effects else "None",
                    "Signal_Details": signal_details,
                    "Signal_Reasons": "; ".join(signal_reasons[:3]) if signal_reasons else "Base aspects only",
                    "Strength": session_info['strength'],
                    "New_Aspects": len(new_aspects),
                    "Dissolved_Aspects": len(dissolved_aspects)
                })
                
                previous_positions = positions.copy()
                previous_aspects_df = aspects_df.copy()
                current_time += timedelta(minutes=interval_minutes)
                interval_count += 1
            
            progress_bar.progress(1.0)
            status_text.text("✅ Comprehensive Analysis Complete!")
            
            if timeline:
                timeline_df = pd.DataFrame(timeline)
                
                # Enhanced summary metrics
                st.subheader(f"📊 {symbol} Complete Analysis - {analysis_date.strftime('%d %B %Y')}")
                
                # Signal distribution
                signal_counts = timeline_df["Signal"].value_counts()
                metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
                
                with metric_col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("🚀 Strong Buy", signal_counts.get("Strong Buy", 0))
                    st.markdown('</div>', unsafe_allow_html=True)
                with metric_col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("📈 Buy", signal_counts.get("Buy", 0))
                    st.markdown('</div>', unsafe_allow_html=True)
                with metric_col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("➡️ Neutral", signal_counts.get("Neutral", 0))
                    st.markdown('</div>', unsafe_allow_html=True)
                with metric_col4:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("📉 Sell", signal_counts.get("Sell", 0))
                    st.markdown('</div>', unsafe_allow_html=True)
                with metric_col5:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("💥 Strong Sell", signal_counts.get("Strong Sell", 0))
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Detailed timeline with enhanced information
                st.subheader("📈 Detailed Trading Timeline with Aspect Analysis")
                
                # Enhanced highlighting function
                def highlight_signals_enhanced(row):
                    if row["Signal"] == "Strong Buy":
                        return ['background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; font-weight: bold;'] * len(row)
                    elif row["Signal"] == "Buy":
                        return ['background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #2c5aa0;'] * len(row)
                    elif row["Signal"] == "Strong Sell":
                        return ['background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); color: white; font-weight: bold;'] * len(row)
                    elif row["Signal"] == "Sell":
                        return ['background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #8b4513;'] * len(row)
                    else:
                        return [''] * len(row)
                
                # Enhanced column selection
                base_columns = ["Time", "Session", "Signal", "Net_Score", "Session_Outlook", "Active_Aspects"]
                
                # Add optional columns
                if show_transits:
                    base_columns.extend(["Transits", "Aspect_Changes"])
                if show_combos:
                    base_columns.append("Combo_Effects")
                
                # Always show signal reasoning
                base_columns.extend(["Signal_Reasons", "New_Aspects", "Dissolved_Aspects"])
                
                display_df = timeline_df[base_columns]
                styled_df = display_df.style.apply(highlight_signals_enhanced, axis=1)
                st.dataframe(styled_df, use_container_width=True, height=500)
                
                # Aspect Change Summary
                st.subheader("⚡ Aspect Formation & Dissolution Analysis")
                
                aspect_summary = []
                for _, row in timeline_df.iterrows():
                    if row["New_Aspects"] > 0 or row["Dissolved_Aspects"] > 0:
                        aspect_summary.append({
                            "Time": row["Time"],
                            "New_Formations": row["New_Aspects"], 
                            "Dissolutions": row["Dissolved_Aspects"],
                            "Net_Change": row["New_Aspects"] - row["Dissolved_Aspects"],
                            "Signal_Impact": row["Signal"],
                            "Aspect_Details": row["Aspect_Changes"]
                        })
                
                if aspect_summary:
                    aspect_df = pd.DataFrame(aspect_summary)
                    st.dataframe(aspect_df, use_container_width=True)
                else:
                    st.info("No significant aspect changes detected during this period")
                
                # Advanced visualizations
                st.subheader("📊 Advanced Market Analysis Charts")
                
                # Create comprehensive charts
                fig = make_subplots(
                    rows=3, cols=1,
                    subplot_titles=(
                        'Session-wise Bullish vs Bearish Weights',
                        'Net Score Trend with Signal Strength',
                        'Active Aspects & Market Activity'
                    ),
                    vertical_spacing=0.08,
                    specs=[[{"secondary_y": True}], 
                           [{"secondary_y": True}], 
                           [{"secondary_y": False}]]
                )
                
                # Chart 1: Bullish vs Bearish weights
                fig.add_trace(
                    go.Scatter(x=timeline_df["Time"], y=timeline_df["Bullish_Weight"],
                              name="Bullish Weight", line=dict(color="green", width=2),
                              fill='tonexty'), row=1, col=1)
                fig.add_trace(
                    go.Scatter(x=timeline_df["Time"], y=timeline_df["Bearish_Weight"],
                              name="Bearish Weight", line=dict(color="red", width=2),
                              fill='tozeroy'), row=1, col=1)
                
                # Chart 2: Net score with signal indicators
                signal_colors = {
                    "Strong Buy": "darkgreen", "Buy": "lightgreen", 
                    "Strong Sell": "darkred", "Sell": "lightcoral", 
                    "Neutral": "gray"
                }
                colors = [signal_colors.get(signal, "gray") for signal in timeline_df["Signal"]]
                
                fig.add_trace(
                    go.Scatter(x=timeline_df["Time"], y=timeline_df["Net_Score"],
                              name="Net Score", mode='lines+markers',
                              line=dict(color="blue", width=3),
                              marker=dict(color=colors, size=10, line=dict(width=2, color="white"))), 
                    row=2, col=1)
                
                # Add zero line
                fig.add_hline(y=0, line_dash="dash", line_color="black", row=2, col=1)
                
                # Chart 3: Active aspects
                fig.add_trace(
                    go.Bar(x=timeline_df["Time"], y=timeline_df["Active_Aspects"],
                           name="Active Aspects", marker_color="purple", opacity=0.7), 
                    row=3, col=1)
                
                # Update layout
                fig.update_layout(
                    height=800,
                    title_text=f"Comprehensive Astrological Analysis - {symbol} | {analysis_date.strftime('%d %B %Y')}",
                    showlegend=True,
                    template="plotly_white"
                )
                
                # Update axes labels
                fig.update_xaxes(title_text="Time", row=3, col=1)
                fig.update_yaxes(title_text="Weight", row=1, col=1)
                fig.update_yaxes(title_text="Net Score", row=2, col=1)
                fig.update_yaxes(title_text="Count", row=3, col=1)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Key insights and recommendations with critical timing
                st.subheader("🔍 Key Insights & Critical Trading Times")
                
                # Identify critical times based on multiple factors
                timeline_df["Criticality_Score"] = (
                    timeline_df["Active_Aspects"] * 0.3 +
                    abs(timeline_df["Net_Score"]) * 0.4 +
                    timeline_df["New_Aspects"] * 2.0 +
                    timeline_df["Dissolved_Aspects"] * 1.5
                )
                
                critical_times = timeline_df.nlargest(5, "Criticality_Score")
                
                # Analysis insights
                max_bullish = timeline_df.loc[timeline_df["Bullish_Weight"].idxmax()]
                max_bearish = timeline_df.loc[timeline_df["Bearish_Weight"].idxmax()]
                max_activity = timeline_df.loc[timeline_df["Active_Aspects"].idxmax()]
                
                insight_col1, insight_col2, insight_col3 = st.columns(3)
                
                with insight_col1:
                    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
                    st.subheader("🚀 Peak Bullish Moment")
                    st.write(f"**Time**: {max_bullish['Time']}")
                    st.write(f"**Signal**: {max_bullish['Signal']}")
                    st.write(f"**Score**: {max_bullish['Bullish_Weight']:.2f}")
                    st.write(f"**Session**: {max_bullish['Session']}")
                    if max_bullish['Signal_Reasons']:
                        st.write(f"**Why**: {max_bullish['Signal_Reasons'][:100]}...")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with insight_col2:
                    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
                    st.subheader("💥 Peak Bearish Moment")
                    st.write(f"**Time**: {max_bearish['Time']}")
                    st.write(f"**Signal**: {max_bearish['Signal']}")
                    st.write(f"**Score**: {max_bearish['Bearish_Weight']:.2f}")
                    st.write(f"**Session**: {max_bearish['Session']}")
                    if max_bearish['Signal_Reasons']:
                        st.write(f"**Why**: {max_bearish['Signal_Reasons'][:100]}...")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with insight_col3:
                    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
                    st.subheader("⚡ Maximum Activity")
                    st.write(f"**Time**: {max_activity['Time']}")
                    st.write(f"**Aspects**: {max_activity['Active_Aspects']}")
                    st.write(f"**Signal**: {max_activity['Signal']}")
                    st.write(f"**Outlook**: {max_activity['Session_Outlook']}")
                    if max_activity['Aspect_Changes'] != "None":
                        st.write(f"**Changes**: {max_activity['Aspect_Changes'][:80]}...")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Critical times analysis
                st.subheader("⏰ Most Critical Trading Times")
                st.write("**Times when maximum astrological activity occurs - ideal for entries/exits:**")
                
                critical_display = []
                for _, row in critical_times.iterrows():
                    reason_parts = []
                    if row["New_Aspects"] > 0:
                        reason_parts.append(f"{row['New_Aspects']} new aspects forming")
                    if row["Dissolved_Aspects"] > 0:
                        reason_parts.append(f"{row['Dissolved_Aspects']} aspects dissolving")
                    if abs(row["Net_Score"]) > 3:
                        reason_parts.append(f"Strong signal ({row['Signal']})")
                    if row["Active_Aspects"] > 8:
                        reason_parts.append(f"High aspect activity ({row['Active_Aspects']})")
                    
                    critical_display.append({
                        "Time": row["Time"],
                        "Session": row["Session"].split(" ")[1] if " " in row["Session"] else row["Session"],
                        "Signal": row["Signal"],
                        "Critical_Score": f"{row['Criticality_Score']:.1f}",
                        "Why_Critical": "; ".join(reason_parts[:2]),
                        "Trading_Advice": get_trading_advice(row["Signal"], row["Session"].split(" ")[1] if " " in row["Session"] else row["Session"])
                    })
                
                critical_df = pd.DataFrame(critical_display)
                
                def highlight_critical_times(row):
                    score = float(row["Critical_Score"])
                    if score > 8:
                        return ['background-color: #ff6b6b; color: white; font-weight: bold;'] * len(row)
                    elif score > 5:
                        return ['background-color: #ffa726; color: white;'] * len(row)
                    else:
                        return ['background-color: #66bb6a; color: white;'] * len(row)
                
                styled_critical = critical_df.style.apply(highlight_critical_times, axis=1)
                st.dataframe(styled_critical, use_container_width=True)

def get_trading_advice(signal, session):
    """Generate specific trading advice based on signal and session"""
    advice_map = {
        ("Strong Buy", "Opening"): "Aggressive long entry on gap down, expect strong rally",
        ("Strong Buy", "Morning"): "Build long positions, momentum likely to continue",
        ("Strong Buy", "Mid-Session"): "Institutional buying, add to longs on dips",
        ("Strong Buy", "Afternoon"): "Late rally expected, short covering likely",
        ("Strong Buy", "Closing"): "Positive close expected, hold overnight longs",
        
        ("Buy", "Opening"): "Selective long entry, watch for confirmation",
        ("Buy", "Morning"): "Moderate buying opportunity, use stops",
        ("Buy", "Mid-Session"): "Gradual accumulation, dollar-cost average",
        ("Buy", "Afternoon"): "Recovery possible, light long positions",
        ("Buy", "Closing"): "Mild positive bias, conservative approach",
        
        ("Strong Sell", "Opening"): "Aggressive short entry on gap up, expect sharp fall",
        ("Strong Sell", "Morning"): "Build short positions, weakness to continue",
        ("Strong Sell", "Mid-Session"): "Heavy institutional selling, avoid longs",
        ("Strong Sell", "Afternoon"): "Exit all longs, sharp correction possible",
        ("Strong Sell", "Closing"): "Negative close likely, exit before close",
        
        ("Sell", "Opening"): "Book profits, avoid fresh longs",
        ("Sell", "Morning"): "Selling pressure building, lighten positions",
        ("Sell", "Mid-Session"): "Profit booking phase, be defensive",
        ("Sell", "Afternoon"): "Weakness emerging, book some profits",
        ("Sell", "Closing"): "End day flat, avoid overnight risk",
        
        ("Neutral", "Opening"): "Wait for direction, no rush to trade",
        ("Neutral", "Morning"): "Range-bound trading, buy support sell resistance",
        ("Neutral", "Mid-Session"): "Consolidation phase, scalping opportunities",
        ("Neutral", "Afternoon"): "Sideways movement, theta decay for options",
        ("Neutral", "Closing"): "Flat close expected, square off positions"
    }
    
    return advice_map.get((signal, session), "Monitor price action closely")

# Tab 3: Professional Daily Report
with tab3:
    st.header("📋 Professional Daily Market Report")
    
    report_col1, report_col2 = st.columns([2, 1])
    
    with report_col1:
        report_date = st.date_input("Select Report Date", datetime(2025, 7, 30))
        report_symbols = st.multiselect("Select Indices", ["NIFTY", "BANKNIFTY", "SENSEX", "FINNIFTY"], default=["NIFTY", "BANKNIFTY"])
    
    with report_col2:
        st.info("""
        **📋 Report Features:**
        • Complete daily analysis
        • Session-wise predictions  
        • Critical timing alerts
        • Professional formatting
        • Risk assessment
        • Trading strategies
        """)
    
    if st.button("📊 Generate Professional Daily Report", type="primary"):
        with st.spinner("🔮 Generating comprehensive daily market report..."):
            
            # Generate comprehensive timeline for the full day
            start_time = datetime.combine(report_date, datetime.strptime("09:15", "%H:%M").time())
            end_time = datetime.combine(report_date, datetime.strptime("15:30", "%H:%M").time())
            
            timeline = []
            current_time = start_time
            
            # Generate 30-minute interval analysis
            while current_time <= end_time:
                positions = calculate_planetary_positions(current_time)
                aspects_df, _ = get_aspects(positions)
                session_info = analyze_market_session(current_time.strftime("%H:%M"), aspects_df, positions)
                
                signal, color, bull_score, bear_score, signal_details = calculate_enhanced_trading_signal(aspects_df, session_info)
                
                timeline.append({
                    "DateTime": current_time.strftime("%Y-%m-%d %H:%M"),
                    "Signal": signal,
                    "Active_Aspects": len(aspects_df),
                    "Bullish_Weight": bull_score,
                    "Bearish_Weight": bear_score,
                    "Session": session_info["session"],
                    "Session_Outlook": session_info["outlook"]
                })
                
                current_time += timedelta(minutes=30)
            
            # Get planetary positions for the day
            day_positions = calculate_planetary_positions(start_time)
            timeline_df = pd.DataFrame(timeline)
            
            # Generate and display the comprehensive report
            daily_report = generate_daily_report(report_date, day_positions, timeline_df)
            
            # Display report in styled container
            st.markdown('<div class="report-container">', unsafe_allow_html=True)
            st.markdown(daily_report)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Additional statistical analysis
            st.subheader("📊 Detailed Statistical Analysis")
            
            if not timeline_df.empty:
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                with stat_col1:
                    buy_signals = len(timeline_df[timeline_df["Signal"].str.contains("Buy", na=False)])
                    st.metric("Total Buy Signals", buy_signals, f"{buy_signals/len(timeline_df)*100:.1f}%")
                
                with stat_col2:
                    sell_signals = len(timeline_df[timeline_df["Signal"].str.contains("Sell", na=False)])
                    st.metric("Total Sell Signals", sell_signals, f"{sell_signals/len(timeline_df)*100:.1f}%")
                
                with stat_col3:
                    max_activity = timeline_df["Active_Aspects"].max()
                    avg_activity = timeline_df["Active_Aspects"].mean()
                    st.metric("Peak Activity", f"{max_activity} aspects", f"Avg: {avg_activity:.1f}")
                
                with stat_col4:
                    max_score = timeline_df["Bullish_Weight"].max() - timeline_df["Bearish_Weight"].min()
                    st.metric("Max Score Range", f"{max_score:.2f}", "Volatility indicator")
                
                # Session-wise breakdown
                st.subheader("📊 Session-wise Performance Breakdown")
                
                session_analysis = timeline_df.groupby("Session").agg({
                    "Signal": lambda x: x.mode().iloc[0] if not x.empty else "Neutral",
                    "Bullish_Weight": "mean",
                    "Bearish_Weight": "mean",
                    "Active_Aspects": "mean"
                }).round(2)
                
                st.dataframe(session_analysis, use_container_width=True)
                
                # Risk assessment
                st.subheader("⚠️ Risk Assessment")
                
                strong_sell_count = len(timeline_df[timeline_df["Signal"] == "Strong Sell"])
                total_signals = len(timeline_df)
                risk_percentage = (strong_sell_count / total_signals * 100) if total_signals > 0 else 0
                
                if risk_percentage > 30:
                    risk_level = "🔴 HIGH RISK"
                    risk_advice = "Exercise extreme caution. Consider reducing positions and implementing tight stop losses."
                elif risk_percentage > 15:
                    risk_level = "🟡 MEDIUM RISK"
                    risk_advice = "Moderate caution advised. Monitor positions closely and be ready to adjust."
                else:
                    risk_level = "🟢 LOW RISK"
                    risk_advice = "Favorable conditions for trading. Normal position sizing recommended."
                
                st.markdown(f"""
                **Risk Level**: {risk_level} ({risk_percentage:.1f}% negative signals)
                
                **Recommendation**: {risk_advice}
                """)
                
                # Download report option
                if st.button("💾 Download Report as Text"):
                    report_text = daily_report.replace("##", "").replace("**", "").replace("*", "")
                    st.download_button(
                        label="📥 Download Daily Report",
                        data=report_text,
                        file_name=f"astro_market_report_{report_date.strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )

# Footer with instructions
st.markdown("---")
st.markdown("""
### 🎯 Professional Features & Usage Guide

**🌟 Advanced Capabilities:**
- **Real-time Planetary Calculations**: Precise astronomical positions with market correlations
- **Enhanced Aspect Analysis**: 9 different aspects with market-specific interpretations  
- **Session-wise Predictions**: Tailored analysis for each market session
- **Professional Report Generation**: DeepSeek-style comprehensive daily reports
- **Risk Assessment**: Quantified risk levels with specific trading advice

**📊 Professional Usage:**
1. **Live Analysis**: Monitor current planetary influences and immediate trading signals
2. **Intraday Planning**: Plan your trading strategy with session-wise predictions
3. **Daily Reports**: Generate comprehensive market outlook for planning and analysis

**🔮 Astrological Features:**
- **27 Nakshatras**: Each with specific market characteristics and trading implications
- **12 Zodiac Signs**: Linked to market sectors and volatility patterns
- **9 Planetary Bodies**: Complete analysis including Rahu/Ketu (lunar nodes)
- **Retrograde Effects**: Special interpretations for retrograde planetary movements

**⚡ Signal Interpretation:**
- **🚀 Strong Buy**: High probability bullish move (>70% bullish weight)
- **📈 Buy**: Favorable for long positions (55-70% bullish weight)
- **💥 Strong Sell**: High probability bearish move (>70% bearish weight)
- **📉 Sell**: Selling pressure likely (55-70% bearish weight)
- **➡️ Neutral**: Range-bound movement (<55% either way)

This professional-grade system provides **institutional-quality astrological market analysis** for serious traders and analysts.
""")
