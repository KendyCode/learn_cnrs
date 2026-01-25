import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

colonnes_automate = ["NUMERO_E", "HEURE_E", "MINUTE_E","SECONDE_E", ]
colonnes_programmation = ['No_Pas', 'mn', 'secondes', 'no h', 'no jours', 'TEMP_CEL', 'REGUL_ECORIUM', 'T_ECOR_FOND', 'T_ECOR_INF', 'T_ECOR_SUP', 'REGUL_HYG', 'HYG_CEL', 'REGUL_PRESSION', 'PRESSION', 'REGUL_C', 'C', 'REGUL_O', 'O', 'REGUL_N', 'N', 'REGUL_X', 'X', 'HAUT_ECOLUX', 'INT_ECOLUX', 'CONFIG_ECOLUX', 'INT_PLUIE', 'VITESSE_VENT', 'VENT_LATERAL_UN', 'VENT_LATERAL_DEUX', 'VENT_LATERAL_TROIS', 'VENT_LATERAL_QUATRE', 'INT_VENT_LAT', 'RENO_AIR', 'EVENT Chromato', '', 'CONFIG_MES_INCUB', 'ACTION_1', 'ACTION_2', 'ACTION_3', 'ACTION_4', 'ACTION_5', 'ACTION_6', 'ACTION_7', 'ACTION_8', 'ACTION_9', 'ACTION_10', 'ACTION_11', 'ACTION_12', 'ACTION_13', 'ACTION_14', 'ACTION_15', 'TEMP_PLUIE', 'CHROMATO', 'EV_VIDANGE_ECORIUM', 'VIDANGE_CANIVEAU', 'EV_VIDANGE_CLIM', '', 'MAX T', 'MIN T', 'MAX HR', 'MIN HR', 'tests valeurs Temp', 'tests valeurs Hum', 'MARCHE', 'HYG_Corrigée pour Temp < 0', 'Min Temp', 'Max Temp', 'Temp Mode Mesure']



df_automate = pd.DataFrame(columns=colonnes_automate)
df_programmation = pd.DataFrame(columns=colonnes_programmation)

# NO PAS
df_programmation.at[0, 'No_Pas'] = 1

# On remplit les cellules suivantes avec la formule Excel (en texte)
# Attention : dans Excel, la ligne 2 correspond à l'index 0 de Pandas + les en-têtes
for i in range(1, 10):
    excel_row = i + 1  # Pour pointer sur la ligne précédente dans Excel
    df_programmation.at[i, 'No_Pas'] = f"=A{excel_row}+1"

# Secondes
df_programmation.at[0, 'secondes'] = 0
for i in range(1, 10):
    excel_row = i + 1  # Pour pointer sur la ligne précédente dans Excel
    df_programmation.at[i, 'secondes'] = f"=C{excel_row}+300"

# mn
for i in range(10):
    # i commence à 0, donc i + 2 = 2 (la première ligne de données dans Excel)
    df_programmation.at[i, 'mn'] = f"=MOD(INT(C{i+2}/60),60)"

# no h
for i in range(10):
    df_programmation.at[i, 'no h'] = f"=INT(C{i+2}/3600)"

# no jours
for i in range(10):
    df_programmation.at[i, 'no jours'] = f"=INT(D{i+2}/24)+1"

ma_liste = [22.0, 0, 22.0, 22.0, 22.0, 1, 60, 0, 0, 1, 450, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 60, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0.0]
df_programmation.iloc[0:10, 5:57] = ma_liste



# Utilisation de ExcelWriter
with pd.ExcelWriter('Road_to_Ecolab.xlsx') as writer:
    df_automate.to_excel(writer, sheet_name='Automate', index=False)
    df_programmation.to_excel(writer, sheet_name='Programmation', index=False)




print("Done")