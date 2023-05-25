from flask import Flask
from app import db



class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_ID = db.Column(db.String)
    name = db.Column(db.String)
    email = db.Column(db.String)
    Profilepicture = db.Column(db.String)

class games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    downloadable = db.Column(db.String)
    genre = db.Column(db.String)
    filename = db.Column(db.String)
    dirname = db.Column(db.String)
    dirpath = db.Column(db.String)
    splashscreen = db.Column(db.String)
    Game_image_1 = db.Column(db.String)
    Game_image_2 = db.Column(db.String)
    Game_image_3 = db.Column(db.String)
    link = db.Column(db.String)

