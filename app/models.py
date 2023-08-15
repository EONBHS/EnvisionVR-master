from flask import Flask
from app import db



class User(db.Model): 
    """The User Class, contains information on the user supplied by their google account when they login."""
    id = db.Column(db.Integer, primary_key=True)
    google_ID = db.Column(db.String)
    name = db.Column(db.String)
    email = db.Column(db.String)
    Profilepicture = db.Column(db.String)

class Games(db.Model):
    """The Games Class contains information supplied by the user about their game."""
    id = db.Column(db.Integer, primary_key=True)
    User_ID = db.Column(db.Integer, db.ForeignKey("user.google_ID"))
    name = db.Column(db.String)
    description = db.Column(db.String)
    downloadable = db.Column(db.Boolean)
    genre = db.Column(db.String)
    filename = db.Column(db.String)
    dirname = db.Column(db.String)
    dirpath = db.Column(db.String)
    splashscreen = db.Column(db.String)
    image1 = db.Column(db.String)
    image2 = db.Column(db.String)
    user = db.relationship("User",
    backref="Game") 

class Jams(db.Model):
    """The Jam Class contains information on the game jam."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    startdate = db.Column(db.String)
    enddate = db.Column(db.String)
    theme = db.Column(db.String)
    image = db.Column(db.String)
    game = db.relationship("Games",
    backref="Jam")

