import pandas as pd

# Votre chargement
df = pd.read_excel('Template-Consignes-V3.0.xlsx')
colonnes_choisies = df.loc[:, 'TEMP_CEL':'EV_VIDANGE_CLIM']

# 1. Extraire la première ligne de données (index 0)
premiere_ligne = colonnes_choisies.iloc[0]

# --- LE DICTIONNAIRE ---
# Clé = Nom de la colonne, Valeur = donnée de la ligne 1
dict_valeurs = premiere_ligne.to_dict()

# --- LE TABLEAU (LISTE) ---
# Uniquement les valeurs, dans l'ordre des colonnes
liste_valeurs = premiere_ligne.tolist()


# --- AFFICHAGE ---
print("--- DICTIONNAIRE DE LA 1ère LIGNE ---")
print(dict_valeurs)

print("\n--- TABLEAU DE LA 1ère LIGNE ---")
print(liste_valeurs)
