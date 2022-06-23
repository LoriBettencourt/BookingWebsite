from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    # This is a dropdown. S/b nullable=false anyway?
    state = db.Column(db.String(120))
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # Revisit this. Had false but saw True in another file
    looking_for_talent = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue',
                            lazy=True, cascade='all, delete-orphan')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist',
                            lazy=True, cascade='all, delete-orphan')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    show_date_time = db.Column(db.DateTime())