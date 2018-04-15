import database as db
from flask import Flask
import sqlalchemy as sa
import datetime

class User(db.Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    date = sa.Column(sa.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return '<Date %r>' % self.date
