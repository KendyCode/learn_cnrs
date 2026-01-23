from sqlalchemy import create_engine

# 1. Configuration des paramètres
USER = "kendy"
PASSWORD = "root"
HOST = "localhost"  # ou l'IP de votre serveur
PORT = "3306"
DB_NAME = "test_alchemy"

# 2. Création de l'URL de connexion
DATABASE_URL = f"mariadb+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

# 3. Création de l'engine
engine = create_engine(DATABASE_URL)

# 4. Test de la connexion
try:
    conn =engine.connect()
    print("Sucess!")
except Exception as ex:
    print(ex)

db = SQLAlchemy()

class Climate(db.Model):
    __tablename__ = "climates"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(32), unique=True, nullable=False)
    longitude = db.Column(db.Numeric(9, 6), nullable=False)
    latitude = db.Column(db.Numeric(9, 6), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    time_interval = db.Column(db.String(100), nullable=False)
    params = db.Column(db.Text, nullable=False)
    file_csv = db.Column(db.String(255), nullable=False)
    climate_type = db.Column(db.String(100), nullable=True)
    meta = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)