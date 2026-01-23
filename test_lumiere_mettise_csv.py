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

# # Remplace temporairement ta section de récupération API par ceci :
# data = {
#     "hourly": {
#         "time": [
#             # 2020 : 3 premières heures du 01/01
#             "2020-01-01T00:00", "2020-01-01T01:00", "2020-01-01T02:00",
#             # 2021 : 3 premières heures du 01/01
#             "2021-01-01T00:00", "2021-01-01T01:00", "2021-01-01T02:00",
#             # 2022 : 3 premières heures du 01/01
#             "2022-01-01T00:00", "2022-01-01T01:00", "2022-01-01T02:00"
#         ],
#         "temperature_2m": [
#             10.0, 16.0, 10.0,  # 2020
#             20.0, 26.0, 20.0,  # 2021
#             30.0, 36.0, 30.0   # 2022
#         ],
#         "precipitation": [0.0, 1.0, 0.0, 0.0, 2.0, 0.0, 0.0, 3.0, 0.0],
#         "relative_humidity_2m": [50] * 9,
#         "dew_point_2m": [5] * 9,
#         "pressure_msl": [1013] * 9,
#         "surface_pressure": [1010] * 9,
#         "et0_fao_evapotranspiration": [0.1] * 9,
#         "wind_speed_10m": [10] * 9,
#         "wind_direction_10m": [180, 180, 180, 200, 200, 200, 220, 220, 220],
#         "direct_radiation": [0, 100, 0, 0, 200, 0, 0, 300, 0],
#         "direct_radiation_instant": [0, 100, 0, 0, 200, 0, 0, 300, 0]
#     }
# }

# --- ZONE DE VÉRIFICATION DÉTAILLÉE (SANS ARRONDI) ---
print("--- ANALYSE DES 01 JANVIER PAR ANNÉE ---")

for annee in [2020, 2021, 2022]:
    print(f"\n================= ANNÉE {annee} =================")

    # Isolation des 24h du 01/01 pour l'année spécifique
    donnees_jour = df[(df['annee'] == annee) & (df['jour_mois'] == '01-01')]

    # Affichage du détail des 24 heures (Température)
    print(f"Détail des 24h du 01/01/{annee} :")
    print(donnees_jour[['temperature_2m']])

    # Calcul de l'addition (Somme)
    somme = donnees_jour['temperature_2m'].sum()
    print(f"\n> ADDITION (Somme des 24h) : {somme}")

    # Calcul de la moyenne journalière
    moyenne_journaliere = donnees_jour['temperature_2m'].mean()
    print(f"> MOYENNE du jour          : {moyenne_journaliere}")

print("\n================================================")
# -----------------------------------------------------