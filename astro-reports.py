import swisseph as swe
import datetime
import pandas as pd

# Nakshatra data
nakshatras = [
    ("Ashwini", 0, 13+20/60), ("Bharani", 13+20/60, 26+40/60), ("Krittika", 26+40/60, 40),
    ("Rohini", 40, 53+20/60), ("Mrigashira", 53+20/60, 66+40/60), ("Ardra", 66+40/60, 80),
    ("Punarvasu", 80, 93+20/60), ("Pushya", 93+20/60, 106+40/60), ("Ashlesha", 106+40/60, 120),
    ("Magha", 120, 133+20/60), ("Purva Phalguni", 133+20/60, 146+40/60), ("Uttara Phalguni", 146+40/60, 160),
    ("Hasta", 160, 173+20/60), ("Chitra", 173+20/60, 186+40/60), ("Swati", 186+40/60, 200),
    ("Vishakha", 200, 213+20/60), ("Anuradha", 213+20/60, 226+40/60), ("Jyeshtha", 226+40/60, 240),
    ("Mula", 240, 253+20/60), ("Purva Ashadha", 253+20/60, 266+40/60), ("Uttara Ashadha", 266+40/60, 280),
    ("Shravana", 280, 293+20/60), ("Dhanishta", 293+20/60, 306+40/60), ("Shatabhisha", 306+40/60, 320),
    ("Purva Bhadrapada", 320, 333+20/60), ("Uttara Bhadrapada", 333+20/60, 346+40/60), ("Revati", 346+40/60, 360)
]

# Zodiac signs
zodiac_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Function to calculate Nakshatra and Pada
def get_nakshatra_pada(degree):
    for nak, start, end in nakshatras:
        if start <= degree < end:
            pada = int((degree - start) // (13+20/60 / 4)) + 1
            return nak, pada
    return "Unknown", 0

# Function to get zodiac sign
def get_zodiac_sign(degree):
    sign_index = int(degree // 30)
    return zodiac_signs[sign_index]

# Function to calculate planetary positions
def get_planetary_positions(date, time, location="New Delhi"):
    # Convert date and time to Julian day
    dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
    
    # Set sidereal mode (Lahiri Ayanamsa)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # Planetary IDs
    planets = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE, "Ketu": swe.MEAN_NODE  # Ketu is 180° opposite Rahu
    }
    
    positions = []
    for planet, pid in planets.items():
        # Calculate position
        lon = swe.calc_ut(jd, pid)[0][0]  # Longitude in degrees
        if planet == "Ketu":
            lon = (lon + 180) % 360  # Ketu is opposite Rahu
        sign = get_zodiac_sign(lon)
        nak, pada = get_nakshatra_pada(lon % 30 + (int(lon // 30) * 30))
        positions.append({
            "Planet": planet,
            "Sign": sign,
            "Degree": f"{int(lon % 30)}° {int((lon % 1) * 60)}'",
            "Nakshatra": nak,
            "Pada": pada
        })
    
    return pd.DataFrame(positions)

# Main execution
date = "2025-07-29"
start_time = "21:29"
end_time = "23:59"
location = "New Delhi"

# Calculate positions for start time
df_start = get_planetary_positions(date, start_time, location)

# Print results
print(f"Vedic Astrology Transit Details for {date} {start_time} IST ({location})")
print(df_start.to_string(index=False))

# Check for changes within the period (simplified)
# For a full period, loop through intervals and detect sign/Nakshatra changes
