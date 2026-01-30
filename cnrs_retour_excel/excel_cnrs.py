import pandas as pd
import numpy as np
import time
import requests
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side

# URL et paramètres
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "start_date": "2013-12-01",
    "end_date": "2025-12-31",
    "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,precipitation,pressure_msl,surface_pressure,et0_fao_evapotranspiration,wind_speed_10m,wind_direction_10m,direct_radiation,direct_radiation_instant",
    "timezone" : "auto"
}



# Récupération des données
response = requests.get(url, params=params)
data = response.json()
# print(data)
print(len(data["hourly"]["time"]))
# print(data["hourly"]["temperature_2m"])
# print(data["hourly"]["relative_humidity_2m"])

start_time = time.time()

colonnes_automate = ['NUMERO_E', 'HEURE_E', 'MINUTE_E', 'SECONDE_E', 'TEMP_CEL', 'REGUL_ECORIUM', 'T_ECOR_FOND', 'T_ECOR_INF', 'T_ECOR_SUP', 'REGUL_HYG', 'HYG_CEL', 'REGUL_PRESSION', 'PRESSION', 'REGUL_CO', 'CO', 'REGUL_O', 'O', 'REGUL_N', 'N', 'REGUL_X', 'X', 'HAUTEUR_ECOLUX', 'INTENSITE_ECOLUX', 'CONFIG_ECOLUX', 'PLUIE', 'VITESSE_VENT_PRINC', 'VENT_LATERAL', 'RENO_AIR', 'CONFIG_MES_INCUB', 'ACTION_UN', 'ACTION_DEUX', 'ACTION_TROIS', 'ACTION_QUATRE', 'ACTION_CINQ', 'ACTION_SIX', 'ACTION_SEPT', 'ACTION_HUIT', 'ACTION_NEUF', 'ACTION_DIX', 'ACTION_ONZE', 'ACTION_DOUZE', 'ACTION_TREIZE', 'ACTION_QUATORZE', 'ACTION_QUINZE', 'TEMP_PLUIE', 'CHROMATO', 'EV_VIDANGE_ECORIUM', 'EV_VIDANGE_CANIVEAU', 'EV_VIDANGE_CLIM', 'CONSIGNE_ESSAI', 'P_VAP_SAT', 'PT_ROSEE', 'HS_PROGR', 'T_BALLON_CHAUD', 'T_BALLON_FROID', 'BALLON_CHAUD_REEL', 'BALLON_FROID_REEL', 'Temp_progr', 'M_A']
colonnes_programmation = ['No_Pas', 'mn', 'secondes', 'no h', 'no jours', 'TEMP_CEL', 'REGUL_ECORIUM', 'T_ECOR_FOND', 'T_ECOR_INF', 'T_ECOR_SUP', 'REGUL_HYG', 'HYG_CEL', 'REGUL_PRESSION', 'PRESSION', 'REGUL_C', 'C', 'REGUL_O', 'O', 'REGUL_N', 'N', 'REGUL_X', 'X', 'HAUT_ECOLUX', 'INT_ECOLUX', 'CONFIG_ECOLUX', 'INT_PLUIE', 'VITESSE_VENT', 'VENT_LATERAL_UN', 'VENT_LATERAL_DEUX', 'VENT_LATERAL_TROIS', 'VENT_LATERAL_QUATRE', 'INT_VENT_LAT', 'RENO_AIR', 'EVENT Chromato', 'Vide_1', 'CONFIG_MES_INCUB', 'ACTION_1', 'ACTION_2', 'ACTION_3', 'ACTION_4', 'ACTION_5', 'ACTION_6', 'ACTION_7', 'ACTION_8', 'ACTION_9', 'ACTION_10', 'ACTION_11', 'ACTION_12', 'ACTION_13', 'ACTION_14', 'ACTION_15', 'TEMP_PLUIE', 'CHROMATO', 'EV_VIDANGE_ECORIUM', 'VIDANGE_CANIVEAU', 'EV_VIDANGE_CLIM', 'Vide_2', 'MAX T', 'MIN T', 'MAX HR', 'MIN HR', 'tests valeurs Temp', 'tests valeurs Hum', 'MARCHE', 'HYG_Corrigée pour Temp < 0', 'Min Temp', 'Max Temp', 'Temp Mode Mesure']


n = len(data["hourly"]["time"])  # Tu pourras changer ça par le nombre de ligne plus tard
df_programmation = pd.DataFrame(index=range(n), columns=colonnes_programmation)
df_automate = pd.DataFrame(columns=colonnes_automate)
df_infos = pd.DataFrame()
df_config = pd.DataFrame()



# --- 1. NO PAS (Optimisé) ---
# Le premier est 1, les autres sont =A{ligne_précédente}+1
df_programmation.at[0, 'No_Pas'] = 1
if n > 1:
    indices_prec = np.arange(2, n + 1).astype(str) # Lignes 2 à n
    df_programmation.loc[1:, 'No_Pas'] = np.char.add("=A", indices_prec) + "+1"

# --- 2. MN & NO H & NO JOURS (Optimisé) ---
# On crée les indices une seule fois pour tout le monde
idx_excel = np.arange(2, n + 2).astype(str)

df_programmation['mn'] = np.char.add("=MOD(INT(C", idx_excel) + "/60),60)"
df_programmation['no h'] = np.char.add("=INT(C", idx_excel) + "/3600)"
df_programmation['no jours'] = np.char.add("=INT(D", idx_excel) + "/24)+1"

# --- 3. SECONDES (Optimisé) ---
df_programmation.at[0, 'secondes'] = 0
if n > 1:
    indices_prec = np.arange(2, n + 1).astype(str)
    df_programmation.loc[1:, 'secondes'] = np.char.add("=C", indices_prec) + "+300"

# --- 4. T_ECOR (Correction) ---
formules_f = np.char.add("=$F", idx_excel)
# On crée une colonne verticale (n lignes, 1 colonne)
colonne_verticale = formules_f[:, np.newaxis]
# On la duplique sur 3 colonnes pour correspondre à cols_ecor
# np.tile(tableau, (répétition_ligne, répétition_colonne))
bloc_formules = np.tile(colonne_verticale, (1, 3))
cols_ecor = ['T_ECOR_FOND', 'T_ECOR_INF', 'T_ECOR_SUP']
df_programmation.loc[:, cols_ecor] = bloc_formules

# Optionnel mais plus robuste pour 50k lignes
cols_parametres = ['TEMP_CEL', 'REGUL_ECORIUM', 'REGUL_HYG', 'HYG_CEL', 'REGUL_PRESSION', 'PRESSION', 'REGUL_C', 'C', 'REGUL_O', 'O', 'REGUL_N', 'N', 'REGUL_X', 'X', 'HAUT_ECOLUX', 'INT_ECOLUX', 'CONFIG_ECOLUX', 'INT_PLUIE', 'VITESSE_VENT', 'VENT_LATERAL_UN', 'VENT_LATERAL_DEUX', 'VENT_LATERAL_TROIS', 'VENT_LATERAL_QUATRE', 'INT_VENT_LAT', 'RENO_AIR', 'EVENT Chromato', 'Vide_1', 'CONFIG_MES_INCUB', 'ACTION_1', 'ACTION_2', 'ACTION_3', 'ACTION_4', 'ACTION_5', 'ACTION_6', 'ACTION_7', 'ACTION_8', 'ACTION_9', 'ACTION_10', 'ACTION_11', 'ACTION_12', 'ACTION_13', 'ACTION_14', 'ACTION_15', 'TEMP_PLUIE', 'CHROMATO', 'EV_VIDANGE_ECORIUM', 'VIDANGE_CANIVEAU', 'EV_VIDANGE_CLIM', 'Vide_2']
ma_liste_complete = [22.0, 0, 1, 60, 0, 0, 1, 450, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 60, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0.0]
df_programmation[cols_parametres] = ma_liste_complete

# 3. ON ÉCRASE UNIQUEMENT TEMP_CEL AVEC LES DONNÉES DE L'API
# Comme n = len(data["hourly"]["temperature_2m"]), les tailles correspondent parfaitement
df_programmation['TEMP_CEL'] = data["hourly"]["temperature_2m"]
df_programmation['HYG_CEL'] = data["hourly"]["relative_humidity_2m"]

#tests valeurs Temp
# On crée l'index décalé (2 + 31 = 33)
idx_decale = (np.arange(2, n + 2) + 31).astype(str)
# Construction de la formule avec IF, OR et des virgules
df_programmation['tests valeurs Temp'] = (
        np.char.add("=IF(OR(F", idx_decale) +
        ">Config!$D$24,F" + idx_decale +
        "<Config!$C$23,BL" + idx_excel +
        "=0,BP" + idx_decale +
        ">Config!$D$24,BP" + idx_decale +
        "<Config!$C$23),\"ERR\",\"OK\")"
)


#tests valeurs Hum
df_programmation['tests valeurs Hum'] = np.char.add("=IF(OR(L", idx_excel) + ">100,L" + idx_excel + "<7,BL" + idx_excel + "=0),\"ERR\",\"OK\")"
df_programmation['MARCHE'] = "=IF(SUM(F" + idx_excel + ":BD" + idx_excel + ")=0,0,1)"
df_programmation['HYG_Corrigée pour Temp < 0'] = (
        "=IF(AND(BP" + idx_excel + "<0,L" + idx_excel + "<=80),80,L" + idx_excel + ")"
)

# On définit l'index de fin (i + 11)
idx_fin = (np.arange(2, n + 2) + 11).astype(str)

# Formule MIN
df_programmation['Min Temp'] = (
        "=MIN(F" + idx_excel + ":F" + idx_fin +
        ",H" + idx_excel + ":H" + idx_fin +
        ",I" + idx_excel + ":I" + idx_fin +
        ",J" + idx_excel + ":J" + idx_fin +
        ",AZ" + idx_excel + ":AZ" + idx_fin + ")"
)

# Formule MAX
df_programmation['Max Temp'] = (
        "=MAX(F" + idx_excel + ":F" + idx_fin +
        ",H" + idx_excel + ":H" + idx_fin +
        ",I" + idx_excel + ":I" + idx_fin +
        ",J" + idx_excel + ":J" + idx_fin +
        ",AZ" + idx_excel + ":AZ" + idx_fin + ")"
)

# idx_prec (idx - 1) pour BP, idx_decale (idx + 31) pour F33
idx_prec = (np.arange(2, n + 2) - 1).astype(str)
idx_decale = (np.arange(2, n + 2) + 31).astype(str)

df_programmation['Temp Mode Mesure'] = (
        "=IF(AJ" + idx_excel + ",BP" + idx_prec + ",F" + idx_decale + ")"
)



###### Automate ######

# 3. Formules pour NUMERO_E (=Programmation!A2, A3, etc.)
df_automate['NUMERO_E'] = np.char.add("=Programmation!A", idx_excel)

# HEURE_E : Pointe vers la colonne D (no h) de Programmation
df_automate['HEURE_E'] = np.char.add("=Programmation!D", idx_excel)

# MINUTE_E : Pointe vers la colonne B (mn) de Programmation
df_automate['MINUTE_E'] = np.char.add("=Programmation!B", idx_excel)

# SECONDE_E : Pointe vers la colonne C (secondes) de Programmation
df_automate['SECONDE_E'] = np.char.add("=Programmation!C", idx_excel)

df_automate['TEMP_CEL'] = np.char.add("=Programmation!F", idx_excel) + "*10"

df_automate['REGUL_ECORIUM'] = np.char.add("=Programmation!G", idx_excel)

df_automate['T_ECOR_FOND'] = (
        "=IF(Programmation!H" + idx_excel +
        "<Config!$B$9,Config!$B$9,Programmation!H" + idx_excel + ")"
)

# Pour la Ceinture Basse (Ligne 10 dans Config)
df_automate['T_ECOR_INF'] = "=IF(Programmation!I" + idx_excel + "<Config!$B$10,Config!$B$10,Programmation!I" + idx_excel + ")"

# Pour la Ceinture Haute (Ligne 11 dans Config)
df_automate['T_ECOR_SUP'] = "=IF(Programmation!J" + idx_excel + "<Config!$B$11,Config!$B$11,Programmation!J" + idx_excel + ")"

df_automate['REGUL_HYG'] = "=Programmation!K" + idx_excel

df_automate['HYG_CEL'] = "=IF(Programmation!L" + idx_excel + ">95,95,Programmation!L" + idx_excel + ")"

df_automate['REGUL_PRESSION'] = "=Programmation!M" + idx_excel
df_automate['PRESSION'] = "=Programmation!N" + idx_excel
df_automate['REGUL_CO'] = "=Programmation!O" + idx_excel
df_automate['CO'] = "=Programmation!P" + idx_excel
df_automate['REGUL_O'] = "=Programmation!Q" + idx_excel
df_automate['O'] = "=Programmation!R" + idx_excel
df_automate['REGUL_N'] = "=Programmation!S" + idx_excel
df_automate['N'] = "=Programmation!T" + idx_excel
df_automate['REGUL_X'] = "=Programmation!U" + idx_excel
df_automate['X'] = "=Programmation!V" + idx_excel
df_automate['HAUTEUR_ECOLUX'] = "=Programmation!W" + idx_excel
df_automate['INTENSITE_ECOLUX'] = "=Programmation!X" + idx_excel
df_automate['CONFIG_ECOLUX'] = "=Programmation!Y" + idx_excel
df_automate['PLUIE'] = "=Programmation!Z" + idx_excel
df_automate['VITESSE_VENT_PRINC'] = "=Programmation!AA" + idx_excel
df_automate['VENT_LATERAL'] = (
        "=Programmation!AB" + idx_excel +
        "+Programmation!AC" + idx_excel + "*2" +
        "+Programmation!AD" + idx_excel + "*4" +
        "+Programmation!AE" + idx_excel + "*8"
)
df_automate['RENO_AIR'] = "=Programmation!AG" + idx_excel
df_automate['CONFIG_MES_INCUB'] = "=Programmation!AJ" + idx_excel
df_automate['ACTION_UN'] = "=Programmation!AK" + idx_excel
df_automate['ACTION_DEUX'] = "=Programmation!AL" + idx_excel
df_automate['ACTION_TROIS'] = "=Programmation!AM" + idx_excel
df_automate['ACTION_QUATRE'] = "=Programmation!AN" + idx_excel
df_automate['ACTION_CINQ']     = "=Programmation!AO" + idx_excel
df_automate['ACTION_SIX']      = "=Programmation!AP" + idx_excel
df_automate['ACTION_SEPT']     = "=Programmation!AQ" + idx_excel
df_automate['ACTION_HUIT']     = "=Programmation!AR" + idx_excel
df_automate['ACTION_NEUF']     = "=Programmation!AS" + idx_excel
df_automate['ACTION_DIX']      = "=Programmation!AT" + idx_excel
df_automate['ACTION_ONZE']     = "=Programmation!AU" + idx_excel
df_automate['ACTION_DOUZE']    = "=Programmation!AV" + idx_excel
df_automate['ACTION_TREIZE']   = "=Programmation!AW" + idx_excel
df_automate['ACTION_QUATORZE'] = "=Programmation!AX" + idx_excel
df_automate['ACTION_QUINZE']   = "=Programmation!AY" + idx_excel
df_automate['TEMP_PLUIE'] = "=Programmation!AZ" + idx_excel + "*10"
df_automate['CHROMATO']            = "=Programmation!BA" + idx_excel
df_automate['EV_VIDANGE_ECORIUM']  = "=Programmation!BB" + idx_excel
df_automate['EV_VIDANGE_CANIVEAU'] = "=Programmation!BC" + idx_excel
df_automate['EV_VIDANGE_CLIM']     = "=Programmation!BD" + idx_excel
df_automate['CONSIGNE_ESSAI']     = 10
df_automate['P_VAP_SAT'] = (
        "=611.213" +
        "+43.53*POWER(Programmation!BP" + idx_excel + ",1)" +
        "+1.598*POWER(Programmation!BP" + idx_excel + ",2)" +
        "+0.0159*POWER(Programmation!BP" + idx_excel + ",3)" +
        "+0.000567*POWER(Programmation!BP" + idx_excel + ",4)"
)
df_automate['PT_ROSEE'] = (
        "=IF(K" + idx_excel + "=0,0," +
        "-241*(LOG10(AY" + idx_excel + "*K" + idx_excel + "/100)-2.7887)/" +
        "((LOG10(AY" + idx_excel + "*K" + idx_excel + "/100)-2.7887-7.625)))"
)

# On crée un index qui commence à 3 au lieu de 2
# np.arange(3, n + 3) génère [3, 4, 5, ...]
idx_automate_decale = np.arange(3, n + 3).astype(str)

# Calcul de l'Humidité Spécifique avec le nouvel index
df_automate['HS_PROGR'] = (
        "=0.622*AY" + idx_automate_decale + "*K" + idx_automate_decale +
        "/(10132500-AY" + idx_automate_decale + "*K" + idx_automate_decale + ")*1000"
)

df_automate['T_BALLON_CHAUD']     = 450
df_automate['T_BALLON_FROID']     = 0
df_automate['BALLON_CHAUD_REEL']     = 45
df_automate['BALLON_FROID_REEL']     = 0

# idx_excel contient ['2', '3', '4', ...]
# On ajoute 31 pour obtenir ['33', '34', '35', ...]
idx_progr = (np.arange(2, n + 2) + 31).astype(str)

df_automate['Temp_progr'] = "=E" + idx_progr + "/10"
df_automate['M_A'] = "=Programmation!BL" + idx_excel


# Tu peux ajouter autant de colonnes que tu veux ici
correspondances_titres = {
    'TEMP_CEL': '=Programmation!F1',
    'REGUL_ECORIUM': '=Programmation!G1',
    'T_ECOR_FOND': '=Programmation!H1',
    'T_ECOR_INF': '=Programmation!I1',
    'T_ECOR_SUP': '=Programmation!J1',
    'REGUL_HYG': '=Programmation!K1',
    'HYG_CEL': '=Programmation!L1'
} # On change juste le nom pour la sortie

# À placer juste avant le bloc "with pd.ExcelWriter"
titres_pour_excel = [correspondances_titres.get(col, col) for col in df_automate.columns]

# Utilisation de ExcelWriter
with pd.ExcelWriter('Diez_Road_to_Ecolab.xlsx', engine='xlsxwriter') as writer:
    df_automate.to_excel(writer, sheet_name='Automate', index=False, header=titres_pour_excel)
    df_programmation.to_excel(writer, sheet_name='Programmation', index=False)
    df_infos.to_excel(writer, sheet_name='Infos', index=False)
    df_config.to_excel(writer, sheet_name='Config', index=False)

    # Récupération de l'objet feuille
    ws_config = writer.sheets['Config']

    # Placer du texte ou des valeurs dans des cases précises
    ws_config.write('A4', "Anticipation (min)")
    ws_config.write('B4', 60)
    ws_config.write('A5', "Fortes Chaleurs")
    ws_config.write('B5', 0)

    # COnfig Regu Eco
    ws_config.write('A7', "Configuration Régulation ECORIUM")
    ws_config.write('B8', "Minimum")
    ws_config.write('B8', "Minimum")
    ws_config.write('A9', "Fond")
    ws_config.write('A10', "Ceinture Basse")
    ws_config.write('A11', "Ceinture Haute")
    ws_config.write('B9', 5)
    ws_config.write('B10', 5)
    ws_config.write('B11', 5)

    ws_config.write('D9', "Temp Pluie")
    ws_config.write('E8', "Minimum")
    ws_config.write('E9', 5)

    #Config Thermo
    ws_config.write('A14', "Configuration Thermofrigopompe")
    ws_config.write('A17', "Ballon Froid")
    ws_config.write('A18', "Ballon Chaud")

    ws_config.write('B16', "Delta Températures (°C)")

    ws_config.write('C15', "Températures Extrèmes Normales")
    ws_config.write('C16', "Minimum")
    ws_config.write('D16', "Maximum")

    ws_config.write('E15', "Températures Extrèmes Fortes")
    ws_config.write('E16', "Minimum")
    ws_config.write('F16', "Maximum")

    ws_config.write('G16', "Offsets Automate")

    ws_config.write('B17', -6.5)
    ws_config.write('C17', -15)
    ws_config.write('D17', 10)
    ws_config.write('E17',-15)
    ws_config.write('F17',5)
    ws_config.write('G17', -6)

    ws_config.write('B18', 10)
    ws_config.write('C18', 20)
    ws_config.write('D18', 55)
    ws_config.write('E18',20)
    ws_config.write('F18',55)
    ws_config.write('G18', 10)

    # Reglage Thermo
    ws_config.write('A23', "Ballon Froid")
    ws_config.write('A24', "Ballon Chaud")

    ws_config.write('B22', "Delta Températures (°C)")

    ws_config.write('C21', "Températures")
    ws_config.write('C22', "Minimum")
    ws_config.write('D22', "Maximum")

    ws_config.write_formula('B23', "=B17-G17")
    ws_config.write_formula('C23', "=IF(B5=1,E17,C17)-G17")
    ws_config.write_formula('D23', "=IF(B5=1,F17,D17)-G17")
    ws_config.write_formula('B24', "=B18-G18")
    ws_config.write_formula('C24', "=IF(B5=1,E18,C18)-G18")
    ws_config.write_formula('D24', "=IF(B5=1,F18,D18)-G18")


    # Feuille Info
    ws_infos = writer.sheets['Infos']

    # --- TITRES (Ligne 30) ---
    ws_infos.write('B30', "T° Ballon Chaud")
    ws_infos.write('C30', "T° Ballon Froid")
    ws_infos.write('D30', "T° Cellule")
    ws_infos.write('E30', "T° ECORIUM Fond")
    ws_infos.write('F30', "T° ECORIUM Bas")
    ws_infos.write('G30', "T° ECORIUM Haut")
    ws_infos.write('H30', "T° Pluie")
    ws_infos.write('I30', "Hygromètrie")
    ws_infos.write('J30', "CO2")

    # --- ÉTIQUETTES (Colonne A) ---
    ws_infos.write('A31', "Minimum")
    ws_infos.write('A32', "Maximum")
    ws_infos.write('A35', "Pas Arrêt")
    ws_infos.write('A36', "Erreur T°")
    ws_infos.write('A37', "Erreur H%")

    # --- FORMULES MINIMUM ---
    ws_infos.write_formula('B31', "=MIN(Automate!BD:BD)")
    ws_infos.write_formula('C31', "=MIN(Automate!BE:BE)")
    ws_infos.write_formula('D31', "=MIN(Programmation!F:F)")
    ws_infos.write_formula('E31', "=MIN(Programmation!H:H)")
    ws_infos.write_formula('F31', "=MIN(Programmation!I:I)")
    ws_infos.write_formula('G31', "=MIN(Programmation!J:J)")
    ws_infos.write_formula('H31', "=MIN(Programmation!AZ:AZ)")
    ws_infos.write_formula('I31', "=MIN(Programmation!L:L)")
    ws_infos.write_formula('J31', "=MIN(Programmation!P:P)")

    # --- FORMULES MAXIMUM ---
    ws_infos.write_formula('B32', "=MAX(Automate!BD:BD)")
    ws_infos.write_formula('C32', "=MAX(Automate!BE:BE)")
    ws_infos.write_formula('D32', "=MAX(Programmation!F:F)")
    ws_infos.write_formula('E32', "=MAX(Programmation!H:H)")
    ws_infos.write_formula('F32', "=MAX(Programmation!I:I)")
    ws_infos.write_formula('G32', "=MAX(Programmation!J:J)")
    ws_infos.write_formula('H32', "=MAX(Programmation!AZ:AZ)")
    ws_infos.write_formula('I32', "=MAX(Programmation!L:L)")
    ws_infos.write_formula('J32', "=MAX(Programmation!P:P)")

    # --- FORMULES DE RECHERCHE D'ERREURS ---
    # Note : MATCH est l'équivalent anglais de EQUIV
    ws_infos.write_formula('B35', "=MATCH(0,Programmation!BL:BL,0)")
    ws_infos.write_formula('B36', '=MATCH("ERR",Programmation!BJ:BJ,0)')
    ws_infos.write_formula('B37', '=MATCH("ERR",Programmation!BK:BK,0)')

























end_time = time.time()
execution_time = end_time - start_time


print(f"Temps d'exécution total : {execution_time:.4f} secondes")