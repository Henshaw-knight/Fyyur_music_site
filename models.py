from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False, default="https://cdn3.vectorstock.com/i/1000x1000/04/42/wedding-ceremony-venue-icon-on-white-background-vector-23040442.jpg")
    facebook_link = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True, cascade='all, delete')

    def __repr__(self):
        return f'<Venue_id: {self.id}, name: {self.name}, shows: {self.shows}>' 


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500), nullable=False, default="https://www.business2community.com/wp-content/uploads/2017/08/blank-profile-picture-973460_640.png")
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True, cascade='all, delete')

    def __repr__(self):
        return f'<Artist_id: {self.id}, name: {self.name}, shows: {self.shows}>'


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String(120), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
