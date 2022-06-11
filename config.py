import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
dialect = 'postgresql'
database_name = 'fyyur_db'
username = 'postgres'
password = 'postgres'
url = 'localhost:5432'


SQLALCHEMY_DATABASE_URI = f'{dialect}://{username}:{password}@{url}/{database_name}'

SQLALCHEMY_TRACK_MODIFICATIONS = False
