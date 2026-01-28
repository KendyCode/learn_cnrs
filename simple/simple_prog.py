import pandas as pd
import requests




# URL et paramètres
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "start_date": "2020-01-01",
    "end_date": "2020-01-02",
    "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,precipitation,pressure_msl,surface_pressure,et0_fao_evapotranspiration,wind_speed_10m,wind_direction_10m,direct_radiation,direct_radiation_instant",
    "timezone" : "auto"
}



# Récupération des données
response = requests.get(url, params=params)
data = response.json()
print(data)
print(data['hourly'])
print(data.get("hourly", {}).get("time")[0])
print(data.get("hourly", {}).get("time")[-1])

#
# # 1. Création du DataFrame
# df = pd.DataFrame(data["hourly"])
#
# # 2. Conversion du temps et indexation
# df['time'] = pd.to_datetime(df['time'])
# df = df.set_index('time')
#
#
#
# # --- 8. EXPORT EN CSV ---
# # On garde index=True pour avoir la nouvelle colonne de temps
# df.to_csv('Time_zone_auto_Simple.csv', index=True, index_label='time', encoding='utf-8')
#
# print("Done")






