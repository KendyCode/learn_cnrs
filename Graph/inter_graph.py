
import pandas as pd
import requests
import json


# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
# url = "https://archive-api.open-meteo.com/v1/archive"
# params = {
#     "latitude": 52.52,
#     "longitude": 13.41,
#     "start_date": "2020-01-01",
#     "end_date": "2020-01-01",
#     # "start_date": "2026-01-06",
#     # "end_date": "2026-01-20",
#     "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,precipitation,pressure_msl,surface_pressure,et0_fao_evapotranspiration,wind_speed_10m,wind_direction_10m,direct_radiation,direct_radiation_instant",
#     "timezone" : "auto"
# }

with open('export_meteo_2j(1) (Copie).json', 'r', encoding='utf-8') as f:
    data = json.load(f)



# response = requests.get(url,params=params)

# data =  response.json()

print(data["hourly"])



def create_data_frame(data):
    # 1. Création du DataFrame
    df = pd.DataFrame(data["hourly"])

    # 2. Convertir 'time' en datetime
    df['time'] = pd.to_datetime(df['time'])

    # 3. Mettre 'time' en index
    df = df.set_index('time')

    # --- ÉTAPE CRUCIALE POUR VOS "NULL" ---
    # On convertit toutes les colonnes en numérique.
    # errors='coerce' transforme les valeurs invalides ou nulles en NaN.
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

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

    # 1. On complète les trous aux extrémités (que si cest null)
    df_resampled = df_resampled.ffill().bfill()

    # 2. SI TOUT ÉTAIT NULL : on met 0 pour éviter un fichier inutilisable
    df_resampled = df_resampled.fillna(0)
    return df_resampled

df_fi = create_data_frame(data)
df_interpoleyyy = interpolation(df_fi)





# # # 6. Arrondi final pour la propreté
# df_final = df_resampled.round(1)





# 5. Export en CSV
# Note : ici on garde index=True (par défaut) car tes dates sont maintenant dans l'index !
df_interpoleyyy.to_csv('K2_1.csv', index=True, encoding='utf-8')
#
# print(df.head())




