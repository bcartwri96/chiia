import database as db
from flask import Flask
import sqlalchemy as sa
import sqlalchemy.orm as sao
import datetime

# User related classes
# ====================
class User(db.Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = sa.Column(sa.Integer, primary_key=True)
    fname = sa.Column(sa.String, nullable=False)
    lname = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=False)
    language = sa.Column(sa.Boolean, nullable=False) # true is english alone, false is mandarin, too.
    pw_hashed = sa.Column(sa.String, nullable=False)
    admin = sa.Column(sa.Boolean)
    confirmed = sa.Column(sa.Boolean, default=False)

    def __repr__(self):
        return '<Details {fname}, {lname}, {email}, with language skills: {language} where account conf = {conf}>'.format(fname=self.fname,
            lname=self.lname, email=self.email, language=self.language, conf=self.confirmed)
    def get_id(self):
        return self.id

    def is_valid(self):
        return self.confirmed

    def is_active(self):
        return self._user.enabled

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def is_admin(self):
        if self.admin:
            return True
        else:
            return False

# Dataset related classes
# =======================

class Dataset(db.Base):
    __tablename__ = 'dataset'
    __table_args__ = {'extend_existing' : True}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    search_type = sa.Column(sa.String, nullable=False)
    user_created = sa.Column(sa.Integer, nullable=False)
    time_created = sa.Column(sa.DateTime, nullable=False)
    year_start = sa.Column(sa.DateTime, nullable=False)
    year_end = sa.Column(sa.DateTime, nullable=False)
    owner = sa.Column(sa.Integer, nullable=False)
    access = sao.relationship("Dataset_Authd", backref='dataset', lazy=True)

class Dataset_Authd(db.Base):
    __tablename__ = 'dataset-authd'
    __table_args__ = {'extend_existing' : True}

    id = sa.Column(sa.Integer, primary_key=True)
    access = sa.Column(sa.Integer, nullable=False)
    dataset_id = sa.Column(sa.Integer, sa.ForeignKey('dataset.id', ondelete='SET NULL'))


# settings page
# =============

class Admin(db.Base):
    __tablename__ = 'admin'
    __table_args__ = {'extend_existing': True}

    id = sa.Column(sa.Integer, primary_key=True)
    search_names = sao.relationship('Search_Names', backref='admin', lazy=True)

class Search_Names(db.Base):
    __tablename__ = 'search-names'
    __table_args__ = {'extend_existing': True}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    admin_id = sa.Column(sa.Integer, sa.ForeignKey('admin.id'), nullable=False)

# tasks
# ======

association_table = sao.Table('association', Base.metadata,
    sa.Column('task', sa.Integer, sa.ForeignKey('tasks.id')),
    sa.Column('transaction', sa.Integer, sa.ForeignKey('transaction.id'))
)

class Task(db.Base):
    __tablename__ = 'tasks'

    id = sa.Column(sa.Integer, primary_key=True)
    nickname = sa.Column(sa.String, nullable=False)
    date_created = sa.Column(sa.DateTime, nullable=False)

    transactions = sao.relationship("transactions", backref="tasks")

class Transactions(db.Base):
    __tablename__ = 'transactions'

    id = sa.Column(sa.Integer, primary_key=True)
    name = ...
