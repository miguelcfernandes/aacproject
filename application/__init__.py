from flask import Flask # Importing the Flask's main instance
from flask_sqlalchemy import SQLAlchemy # https://flask-sqlalchemy.palletsprojects.com/en/2.x/
from flask_bcrypt import Bcrypt # Importing 'Bcrypt' to hash passwords.
from flask_mail import Mail # Importing 'Flask_Mail' to send emails.
from itsdangerous import URLSafeTimedSerializer # Importing 'URLSafeSerializer' to generate timed and URL-friendly serial keys.


app = Flask(__name__) # Creating an instance of the Flask class.
app.secret_key = 'super_secret' # Creating the secret key.
app.config.from_pyfile('mail_server.cfg') # Mail server configuration
db = SQLAlchemy(app) # Creating a database instance.
bcrypt = Bcrypt(app) # Creating an instance of Bcrypt.
mail = Mail(app) # Creating an instance of Flask_Mail.
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY']) # Creating an instance of URLSafeTimedSerializer.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' # Connecting to the database file.
app.config['UPLOAD_FOLDER'] = 'static/media' # Setting up the upload folder


from application import routes