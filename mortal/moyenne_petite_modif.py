import openmeteo_requests
import pandas as pd
import requests
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# URL et paramètres
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "start_date": "2020-01-01",
    "end_date": "2022-12-31",
    "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,precipitation,pressure_msl,surface_pressure,et0_fao_evapotranspiration,wind_speed_10m,wind_direction_10m,direct_radiation,direct_radiation_instant",
    "timezone" : "auto"
}

# Récupération des données
response = requests.get(url, params=params)
data = response.json()
print(data["hourly"])

# # Simulation des données pour test (Remplace la partie API dans ton code)
# data = {
#     "hourly": {
#         "time": [
#             # 2020 (24 heures pour le 01/01)
#             *[f"2020-01-01T{h:02d}:00" for h in range(24)],
#             # 2021 (24 heures pour le 01/01)
#             *[f"2021-01-01T{h:02d}:00" for h in range(24)],
#             # 2022 (24 heures pour le 01/01)
#             *[f"2022-01-01T{h:02d}:00" for h in range(24)],
#         ],
#         "temperature_2m": [
#             *[10] * 24, # Valeurs pour 2020
#             *[20] * 24, # Valeurs pour 2021
#             *[30] * 24, # Valeurs pour 2022
#         ],
#         # Ajout de colonnes vides pour éviter les erreurs avec ton DataFrame actuel
#         "precipitation": [0] * 72,
#         "relative_humidity_2m": [0] * 72,
#         "dew_point_2m": [0] * 72,
#         "pressure_msl": [0] * 72,
#         "surface_pressure": [0] * 72,
#         "et0_fao_evapotranspiration": [0] * 72,
#         "wind_speed_10m": [0] * 72,
#         "wind_direction_10m": [0] * 72,
#         "direct_radiation": [0] * 72,
#         "direct_radiation_instant": [0] * 72
#     }
# }

# 1. Création du DataFrame
df = pd.DataFrame(data["hourly"])

# 2. Conversion du temps et indexation
df['time'] = pd.to_datetime(df['time'])
df = df.set_index('time')

# 3. Création des colonnes de regroupement
df_temp = df.copy()
df_temp['jour_mois'] = df.index.strftime('%m-%d')



# 4. Calcul de la moyenne finale par jour de l'année (Mixe 2020, 2021, 2022)
# On retire la colonne 'annee' pour ne pas calculer sa moyenne
df_moyenne = df_temp.groupby('jour_mois').mean(numeric_only=True)

# 5. Vérification de la valeur finale pour le 01-01 dans le DataFrame de sortie
valeur_finale = df_moyenne.loc['01-01', 'temperature_2m']
print(f"\nVALEUR FINALE DANS LE CSV (Moyenne des 3 ans) pour le 01-01 : {valeur_finale}")

# 6. Export en CSV
df_moyenne.to_csv('ARK27_IIIKatsune_moyenne.csv', index=True, encoding='utf-8')

print("\nFichier '1_moyenne.csv' généré avec succès.")

