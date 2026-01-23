from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from decimal import Decimal

app = Flask(__name__)

username = 'kendy'
password = 'root'
host = '127.0.0.1'
database = 'test_alchemy'

# Configuration de la base de données MariaDB
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODÈLE UNIQUE : CLIMAT ---

class Climat(db.Model):
    __tablename__ = 'climats'

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(32), unique=True, nullable=False)

    # Coordonnées GPS
    longitude = db.Column(db.Numeric(9, 6), nullable=False)
    latitude = db.Column(db.Numeric(9, 6), nullable=False)

    # Dates et temps
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    creation_date= db.Column(db.DateTime, nullable=False)

    # Informations techniques et méta-données
    params = db.Column(db.Text, nullable=False)
    file_csv = db.Column(db.String(255), nullable=False)
    file_ecolab = db.Column(db.String(255), nullable=False)
    climate_type = db.Column(db.String(100), nullable=True)
    meta = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True) # Text au lieu de String pour plus de place

    def __repr__(self):
        return f'<Climat {self.title} (UID: {self.uid})>'

# --- FONCTION D'ENREGISTREMENT ---
def insert_sample_data():
    """Fonction pour insérer une donnée de test"""
    # On vérifie d'abord si cet UID existe déjà pour éviter une erreur
    existing = Climat.query.filter_by(uid="abc-123-xyz").first()
    if existing:
        print("INFO : La donnée avec l'UID 'abc-123-xyz' existe déjà. Pas d'insertion.")
        return

    nouveau_climat = Climat(
        uid="abc-123-xyz",
        longitude=Decimal("3.876715"),
        latitude=Decimal("43.610769"),
        start_date=datetime(2024, 1, 1, 8, 0),
        end_date=datetime(2024, 12, 31, 23, 59),
        creation_date=datetime.now(timezone.utc),
        params='{"sensor": "DHT22", "unit": "Celsius"}',
        file_csv="export_montpellier_2024.csv",
        file_ecolab="config_ecolab_v1.json",
        climate_type="Méditerranéen",
        title="Station Montpellier Sud",
        description="Données récoltées via le module EcoLab v2"
    )

    try:
        db.session.add(nouveau_climat)
        db.session.commit()
        print("SUCCÈS : Enregistrement réussi dans MariaDB !")
    except Exception as e:
        db.session.rollback()
        print(f"ERREUR : Lors de l'enregistrement : {e}")



# --- CRÉATION DE LA TABLE ---
# Ce bloc crée la table 'climats' dans MariaDB si elle n'existe pas encore
with app.app_context():
    db.create_all()

    # Insère les données de test
    insert_sample_data()





if __name__ == "__main__":
    # host='0.0.0.0' permet d'ouvrir le serveur au réseau local
    app.run(debug=True, port=8080)



