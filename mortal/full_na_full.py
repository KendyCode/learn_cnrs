import openmeteo_requests

import pandas as pd
import requests
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "start_date": "2020-01-01",
    "end_date": "2022-12-31",
    "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,precipitation,pressure_msl,surface_pressure,et0_fao_evapotranspiration,wind_speed_10m,wind_direction_10m,direct_radiation,direct_radiation_instant",
}

#sans_colone_time_Datebayof_test_moyenne

response = requests.get(url,params=params)

data =  response.json()

print(data["hourly"])

# 1. Création du DataFrame
df = pd.DataFrame(data["hourly"])

# 2. Convertir la colonne 'time' en type datetime (très important pour l'interpolation ensuite)
df['time'] = pd.to_datetime(df['time'])

# 3. Définir 'time' comme index
df = df.set_index('time')

#--- 4. LOGIQUE DE MOYENNE PAR JOUR DE L'ANNÉE ---

# On crée une colonne temporaire qui contient uniquement le format "MM-DD"
# On utilise .index.strftime car nos dates sont dans l'index
# df['jour_mois'] = df.index.strftime('%m-%d')

# On groupe par cette nouvelle colonne et on calcule la moyenne
# Cela va mixer toutes les années (2020, 2021, etc.) pour chaque jour identique
df_moyenne = df.groupby(df.index.strftime('%m-%d')).mean()





# On retire l'index temporel pour coller à ton format
df_moyenne.to_csv('DATEBAYOF_test_moyenne.csv', index=False)

