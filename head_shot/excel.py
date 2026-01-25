import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import numpy as np



colonnes_automate = ["NUMERO_E", "HEURE_E", "MINUTE_E","SECONDE_E", ]
colonnes_programmation = ['No_Pas', 'mn', 'secondes', 'no h', 'no jours', 'TEMP_CEL', 'REGUL_ECORIUM', 'T_ECOR_FOND', 'T_ECOR_INF', 'T_ECOR_SUP', 'REGUL_HYG', 'HYG_CEL', 'REGUL_PRESSION', 'PRESSION', 'REGUL_C', 'C', 'REGUL_O', 'O', 'REGUL_N', 'N', 'REGUL_X', 'X', 'HAUT_ECOLUX', 'INT_ECOLUX', 'CONFIG_ECOLUX', 'INT_PLUIE', 'VITESSE_VENT', 'VENT_LATERAL_UN', 'VENT_LATERAL_DEUX', 'VENT_LATERAL_TROIS', 'VENT_LATERAL_QUATRE', 'INT_VENT_LAT', 'RENO_AIR', 'EVENT Chromato', 'Vide_1', 'CONFIG_MES_INCUB', 'ACTION_1', 'ACTION_2', 'ACTION_3', 'ACTION_4', 'ACTION_5', 'ACTION_6', 'ACTION_7', 'ACTION_8', 'ACTION_9', 'ACTION_10', 'ACTION_11', 'ACTION_12', 'ACTION_13', 'ACTION_14', 'ACTION_15', 'TEMP_PLUIE', 'CHROMATO', 'EV_VIDANGE_ECORIUM', 'VIDANGE_CANIVEAU', 'EV_VIDANGE_CLIM', 'Vide_2', 'MAX T', 'MIN T', 'MAX HR', 'MIN HR', 'tests valeurs Temp', 'tests valeurs Hum', 'MARCHE', 'HYG_Corrigée pour Temp < 0', 'Min Temp', 'Max Temp', 'Temp Mode Mesure']


n = 10  # Tu pourras changer ça par le nombre de ligne plus tard
df_programmation = pd.DataFrame(index=range(n), columns=colonnes_programmation)
df_automate = pd.DataFrame(columns=colonnes_automate)


# --- 1. NO PAS (Optimisé) ---
# Le premier est 1, les autres sont =A{ligne_précédente}+1
df_programmation.at[0, 'No_Pas'] = 1
if n > 1:
    indices_prec = np.arange(2, n + 1).astype(str) # Lignes 2 à n
    df_programmation.loc[1:, 'No_Pas'] = np.char.add("=A", indices_prec) + "+1"

# --- 2. MN & NO H & NO JOURS (Optimisé) ---
# On crée les indices une seule fois pour tout le monde
idx_excel = np.arange(2, n + 2).astype(str)

df_programmation['mn'] = np.char.add("=MOD(INT(C", idx_excel) + " /60),60)"
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


# ma_liste = [22.0, 0, 22.0, 22.0, 22.0, 1, 60, 0, 0, 1, 450, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 60, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0.0]
# df_programmation.iloc[0:10, 5:57] = ma_liste



# Utilisation de ExcelWriter
with pd.ExcelWriter('Road_to_Ecolab.xlsx') as writer:
    df_automate.to_excel(writer, sheet_name='Automate', index=False)
    df_programmation.to_excel(writer, sheet_name='Programmation', index=False)




print("Done")