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


