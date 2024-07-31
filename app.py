from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
# Enable CORS
CORS(app)
# Import routes after initializing db to avoid circular import
from routes import *

if __name__ == "__main__":
    app.run(debug=True)
