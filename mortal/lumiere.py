import openmeteo_requests
import pandas as pd
import requests
import requests_cache
from retry_requests import retry
from kms_interpolation import interpolation

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

#bon_Garou_moyenne

# Récupération des données
response = requests.get(url, params=params)
data = response.json()
print(data["hourly"])



# 1. Création du DataFrame
df = pd.DataFrame(data["hourly"])

# 2. Conversion du temps et indexation
df['time'] = pd.to_datetime(df['time'])
df = df.set_index('time')


def moyenne_et_interpolation(df):
    # 3. Création des colonnes de regroupement
    df['jour_mois'] = df.index.strftime('%m-%d')
    df['annee'] = df.index.year

    # --- 4. CALCUL DE LA MOYENNE ET REFORMATAGE DE LA DATE ---

    # On calcule la moyenne en ignorant les colonnes non-numériques (comme jour_mois)
    df_moyenne = df.drop(columns=['annee']).groupby('jour_mois').mean(numeric_only=True)

    # Ici, on transforme l'index '01-01' en '2024-01-01T00:00'
    # On utilise 2024 (année bissextile) pour être sûr que le 29 février passe
    df_moyenne.index = pd.to_datetime("2024-" + df_moyenne.index)

    df_resampled = interpolation(df_moyenne)

    # On définit le point de départ
    temps_zero = df_resampled.index[0]

    # On calcule l'écart total (Timedelta) pour chaque ligne
    diff = df_resampled.index - temps_zero
    secondes_totale = diff.total_seconds().astype(int)

    # 1. Pas cumulés : commence à 1 (1, 2, 3...)
    df_resampled['pas_cumule'] = range(1, len(df_resampled) + 1)

    # 2. Jours cumulés : commence à 1 (1 pour le premier jour, 2 pour le second...)
    # On divise par 86400 (secondes dans un jour) et on ajoute 1
    df_resampled['jours_cumules'] = (secondes_totale // 86400) + 1

    # 3. Secondes cumulées : commence à 0
    df_resampled['secondes_cumulees'] = secondes_totale

    # 4. Minutes cumulées : commence à 0
    df_resampled['minutes'] = (secondes_totale // 60) % 60

    # 5. Heures cumulées : commence à 0 (cumul infini : 24, 25, 26...)
    df_resampled['heures_cumulees'] = (secondes_totale // 3600)


    # --- 9.5 RÉORGANISATION ET CHANGEMENT D'INDEX ---

    # 1. On transforme l'index actuel (le temps) en une colonne normale
    df_resampled = df_resampled.reset_index()

    # 2. On supprime la colonne 'time' (et 'jour_mois' si elle existe encore)
    # errors='ignore' permet d'éviter un plantage si la colonne est déjà partie
    df_resampled = df_resampled.drop(columns=['time', 'jour_mois'], errors='ignore')

    # 3. On définit 'pas_cumule' comme le nouvel index
    df_resampled = df_resampled.set_index('pas_cumule')

    # 4. (Optionnel) On réorganise les colonnes de temps restantes pour qu'elles soient au début
    colonnes_temps = ['minutes', 'secondes_cumulees','heures_cumulees', 'jours_cumules']
    autres_colonnes = [c for c in df_resampled.columns if c not in colonnes_temps]
    df_resampled = df_resampled[colonnes_temps + autres_colonnes]

    return df_resampled

fin = moyenne_et_interpolation(df)






# --- 8. EXPORT EN CSV ---
# On garde index=True pour avoir la nouvelle colonne de temps
fin.to_csv('F1_ERR_TIME_ZONE_AUTO_fix_minutes_supprimer_time_avec_sec_heure_etc_interpol_5min_date_fmt_api_base_Garou_moyenne.csv', index=True, index_label='pas_cumule', encoding='utf-8')

print("\nFichier 'Katsune_moyenne.csv' généré avec succès.")






