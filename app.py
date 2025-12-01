from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'djah4#$2hbrq3478bfeb#$F&%/H$_3425fdwf#'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123456789@localhost/FirmaDigital'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de la carpeta de subidas
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'error'

from routes import *

if __name__ == '__main__':
    # Crear carpeta uploads si no existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)