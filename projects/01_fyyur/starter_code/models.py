from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade="all, delete-orphan")

    def __getitem__(self, field):
      return self.__dict__[field]


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False, nullable=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all, delete-orphan")

    def __getitem__(self, field):
      return self.__dict__[field]


class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key = True, nullable = False)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.today())
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable = False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable = False)