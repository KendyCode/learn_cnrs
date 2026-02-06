
import pandas as pd
import requests
import json









with open('export_meteo_sp_1095.json', 'r', encoding='utf-8') as f:
    data = json.load(f)




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

def ajouter_colonnes_temporelles(df_resampled):
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

def calculer_moyenne_annuelle(df):
    """Calcule la moyenne par jour de l'année (ignore l'année réelle)."""
    df_temp = df.copy()
    df_temp['jour_mois'] = df_temp.index.strftime('%m-%d')

    # Moyenne par jour/mois (numeric_only pour éviter les erreurs sur les strings)
    df_moyenne = df_temp.groupby('jour_mois').mean(numeric_only=True)

    # Re-transformation en datetime sur une année pivot (2024 pour le 29 fév)
    df_moyenne.index = pd.to_datetime("2024-" + df_moyenne.index)
    return df_moyenne

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

df = create_data_frame(data)
df_base = calculer_moyenne_annuelle(df)
df_interpole = interpolation(df_base)
df_final = ajouter_colonnes_temporelles(df_interpole)

df_final.to_csv('KR_final_graph.csv', index=True, encoding='utf-8')