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
    # "start_date": "2026-01-06",
    # "end_date": "2026-01-20",
    "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,precipitation,pressure_msl,surface_pressure,et0_fao_evapotranspiration,wind_speed_10m,wind_direction_10m,direct_radiation,direct_radiation_instant",
    "timezone" : "auto"
}

response = requests.get(url,params=params)

data =  response.json()

print(data["hourly"])



def create_data_frame(data):
    # 1. Création du DataFrame
    df = pd.DataFrame(data["hourly"])

    # 2. Convertir la colonne 'time' en type datetime (très important pour l'interpolation ensuite)
    df['time'] = pd.to_datetime(df['time'])

    # 3. Définir 'time' comme index
    df = df.set_index('time')

    return df

def interpolation(df):
    # 4. Création des lignes vides toutes les 5 minutes
    df_resampled = df.resample('5min').asfreq()

    # --- 5. Traitement intelligent par groupes de paramètres ---

    # On définit les règles dans un dictionnaire
    groupes = {
        'linear': ['temperature_2m', 'relative_humidity_2m', 'pressure_msl', 'surface_pressure', 'dew_point_2m', 'et0_fao_evapotranspiration'],
        'ffill': ['wind_direction_10m', 'precipitation'],
        'pchip': ['direct_radiation', 'direct_radiation_instant', 'wind_speed_10m']
    }

    for method, cols in groupes.items():
        # On crée la liste des colonnes présentes (sans compréhension de liste)
        cols_presentes = []
        for c in cols:
            if c in df_resampled.columns:
                cols_presentes.append(c)

        # On applique la méthode si des colonnes correspondantes existent
        if len(cols_presentes) > 0:
            if method == 'linear':
                df_resampled[cols_presentes] = df_resampled[cols_presentes].interpolate(method='linear')
            elif method == 'ffill':
                df_resampled[cols_presentes] = df_resampled[cols_presentes].ffill()
            elif method == 'pchip':
                # pchip est excellent pour les courbes solaires et le vent
                df_resampled[cols_presentes] = df_resampled[cols_presentes].interpolate(method='pchip')
    return df_resampled

df_fi = create_data_frame(data)
df_interpoleyyy = interpolation(df_fi)





# # # 6. Arrondi final pour la propreté
# df_final = df_resampled.round(1)





# 5. Export en CSV
# Note : ici on garde index=True (par défaut) car tes dates sont maintenant dans l'index !
df_interpoleyyy.to_csv('F2_Time_zone_auto_2020_2022_tous_les_params_interpol_adapt_sans_round.csv', index=True, encoding='utf-8')
#
# print(df.head())




