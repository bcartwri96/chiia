# this file defines the models that govern our database.
from flask import Flask as fl
from flask_sqlalchemy import SQLAlchemy
import os
import datetime

#############################################################
# models
#############################################################
from sqlalchemy import Column, Integer, String, DateTime
import code.database as db

class User(db.Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, id=None, date=None):
            self.id = id
            self.date = date

    def __repr__(self):
        return '<User %r>' % (self.date)
