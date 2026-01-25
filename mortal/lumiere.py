import openmeteo_requests
import pandas as pd
import requests
import requests_cache
from retry_requests import retry

# --- 1. CONFIGURATION API ET RÉCUPÉRATION ---
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "start_date": "2020-01-01",
    "end_date": "2022-12-31",
    "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,precipitation,pressure_msl,surface_pressure,et0_fao_evapotranspiration,wind_speed_10m,wind_direction_10m,direct_radiation,direct_radiation_instant",
}

response = requests.get(url, params=params)
data = response.json()

# Création du DataFrame initial
df = pd.DataFrame(data["hourly"])
df['time'] = pd.to_datetime(df['time'])
df = df.set_index('time')

# --- 2. TRAITEMENT DES MOYENNES (Groupement par jour/mois) ---
df['jour_mois'] = df.index.strftime('%m-%d %H:%M') # On garde l'heure pour le groupement
df_moyenne = df.groupby('jour_mois').mean(numeric_only=True)

# Reconstruction d'un index temporel sur une année fictive (2024 bissextile)
df_moyenne.index = pd.to_datetime("2024-" + df_moyenne.index)
df_moyenne = df_moyenne.sort_index()

# --- 3. INTERPOLATION 5 MINUTES ---
# Création des lignes toutes les 5 minutes
df_resampled = df_moyenne.resample('5min').asfreq()

# Application des méthodes d'interpolation par groupe
groupes = {
    'linear': ['temperature_2m', 'relative_humidity_2m', 'pressure_msl', 'surface_pressure', 'dew_point_2m', 'et0_fao_evapotranspiration'],
    'ffill': ['wind_direction_10m', 'precipitation'],
    'pchip': ['direct_radiation', 'direct_radiation_instant', 'wind_speed_10m']
}

for method, cols in groupes.items():
    cols_presentes = [c for c in cols if c in df_resampled.columns]
    if cols_presentes:
        if method == 'linear':
            df_resampled[cols_presentes] = df_resampled[cols_presentes].interpolate(method='linear')
        elif method == 'ffill':
            df_resampled[cols_presentes] = df_resampled[cols_presentes].ffill()
        elif method == 'pchip':
            df_resampled[cols_presentes] = df_resampled[cols_presentes].interpolate(method='pchip')

# Nettoyage final des NaNs restants (début/fin de fichier)
# df_resampled = df_resampled.ffill().bfill()

# --- 4. CALCULS DES TEMPS (CUMULÉS ET CYCLIQUES) ---
temps_zero = df_resampled.index[0]
diff = df_resampled.index - temps_zero
sec_totale = diff.total_seconds().astype(int)

# Création des colonnes demandées
df_resampled['pas_cumule'] = range(1, len(df_resampled) + 1)
df_resampled['jours_cumules'] = (sec_totale // 86400) + 1
df_resampled['secondes_cumulees'] = sec_totale
df_resampled['heures_cumulees'] = (sec_totale // 3600)
df_resampled['minutes'] = (sec_totale // 60) % 60  # Remise à 0 toutes les heures

# --- 5. RÉORGANISATION FINALE (Suppression de 'time') ---
# On sort 'time' de l'index pour pouvoir le supprimer
df_resampled = df_resampled.reset_index()
df_resampled = df_resampled.drop(columns=['time', 'jour_mois'], errors='ignore')

# Définition du pas_cumule comme index final
df_resampled = df_resampled.set_index('pas_cumule')

# Ordre des colonnes de temps au début
colonnes_temps = ['minutes', 'secondes_cumulees', 'heures_cumulees', 'jours_cumules']
autres_cols = [c for c in df_resampled.columns if c not in colonnes_temps]
df_resampled = df_resampled[colonnes_temps + autres_cols]

# --- 6. EXPORT CSV ---
nom_sortie = 'rrr_meteo_final.csv'
df_resampled.to_csv(nom_sortie, index=True, index_label='pas_cumule', encoding='utf-8')

print(f"\nTraitement terminé. Fichier '{nom_sortie}' généré avec succès.")