from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 1. Configuration des paramètres
USER = "kendy"
PASSWORD = "root"
HOST = "localhost"  # ou l'IP de votre serveur
PORT = "3306"
DB_NAME = "test_alchemy"

# 2. Création de l'URL de connexion
app.config['SQLALCHEMY_DATABASE_URI'] = f"mariadb+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
@app.route('/')
def welcome():
    return render_template("welcome.html")

@app.route('/bonjour/<string:name>')
def bonjour(name:str):
    return render_template("bonjour.html", name=name)

if __name__ == "__main__":
    # host='0.0.0.0' permet d'ouvrir le serveur au réseau local
    app.run(debug=True, port=8081)

