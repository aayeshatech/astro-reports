import requests

url = "https://data.astronomics.ai/almanac?date=2025-07-29&location=Ahmedabad"
headers = {"Authorization": "Bearer YOUR_API_KEY"}  # If required
response = requests.get(url, headers=headers)

if response.ok:
    data = response.json()
    print(data)
else:
    print("Error fetching data")
