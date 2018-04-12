"""
The flask application package.
"""

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a1b2cd?><dqw33dw2'
app.config['UPLOAD_FOLDER'] = '/app/uploads'
app.config['DATA_BROKER_URL'] = 'https://gistrest1.herokuapp.com/'
CORS(app)

from API import views