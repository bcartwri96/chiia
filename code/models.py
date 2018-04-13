# this file defines the models that govern our database.
from flask import Flask as fl
from flask_sqlalchemy import SQLAlchemy
import os
import datetime

app = fl(__name__) #instantiate the app
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

db = SQLAlchemy(app)

#############################################################
# models
#############################################################

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, id=None, date=None):
            self.id = id
            self.date = date

    def __repr__(self):
        return '<User %r>' % (self.date)
