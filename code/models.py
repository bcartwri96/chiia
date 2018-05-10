import database as db
from flask import Flask
import sqlalchemy as sa
import sqlalchemy.orm as sao
import datetime
from sqlalchemy.ext.declarative import declared_attr

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

class Tasks(db.Base):
    __tablename__ = 'tasks'
    __table_args__ = {'extend_existing' : True}

    id = sa.Column(sa.Integer, primary_key=True)
    nickname = sa.Column(sa.String, nullable=False)
    date_created = sa.Column(sa.DateTime, nullable=False)
    dataset_owner = sa.Column(sa.Integer, nullable=False)
    # if the stage has moved from a task to the first of the
    # proper stages, we set this true for bookkeeping purposes.
    is_staged = sa.Column(sa.Boolean)


# transactions
# =============

class Transactions(db.Base):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing' : True}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    date = sa.Column(sa.DateTime, nullable=False)
    stage = sa.Column(sa.Integer, nullable=False)
    amount = sa.Column(sa.Float, nullable=False)
    who_assigned = sa.Column(sa.Integer, nullable=False)
    who_previous_stages = sa.Column(sa.PickleType)

    dataset_id = sa.Column(sa.Integer, nullable=False)
    task_id = sa.Column(sa.Integer, nullable=False)
    # will a transaction have a link to the task?
    # I don't think it needs to, but we'll include
    # it for completeness

    # this is the state of each of the transactions.
    # can be done, need a redo or archived.
    state = sa.Column(sa.Integer, nullable=False)


# stages
# ======

# base stage class
class Base_Stage_Task(db.Base):
    __table_args__ = {'extend_existing' : True}
    __abstract__ = True

    # unique identifier for each staid = sa.Column(sa.Integer, primary_key=True)
    # describes the state of the current state with reference
    # to the transaction id
    stage = sa.Column(sa.Integer, nullable=False)
    # speaking of the transaction id, we need to know exactly
    # what the transaction is which we're referring to
    tid = sa.Column(sa.Integer, nullable=False)

class Stage_2(Base_Stage_Task):
    __tablename__ = 'stage_2'
    __table_args__ = {'extend_existing' : True}

    # num times assigned to an analyst
    reviews = sa.Column(sa.Integer, nullable=False)
    # date originally assigned
    date_assigned = sa.Column(sa.DateTime, nullable=False)
    chin_inv_file_no = sa.Column(sa.Float, nullable=False)
    counterpart_file_no = sa.Column(sa.Float)

    # workflow options below
    correspondence_req = sa.Column(sa.Boolean)
    # indicate whether Mandarin is required in the
    # next stage
    mandarin_req = sa.Column(sa.Boolean)
    # if needs to be redone because of a langauge barrier
    redo_by_mandarin = sa.Column(sa.Boolean)
    # IF they select that correspondence is required,
    # then we want to record the following:
    # TODO: add this to the options in the settings page
    type_correspondence = sa.Column(sa.Integer)
    info_from_correspondence = sa.Column(sa.String)
    info_already_found = sa.Column(sa.String)

    # IF they select a new file is created, then we need to
    # record the following:
    pid = sa.Column(sa.Integer)
    legal_name = sa.Column(sa.String)
    linked_iid = sa.Column(sa.Integer)
    nickname_iid = sa.Column(sa.String)
    file_checked_la = sa.Column(sa.Boolean)

class Stage_3(Base_Stage_Task):
    __tablename__ = 'stage_3'

    reviews = sa.Column(sa.Integer,nullable=False)
    date_assigned = sa.Column(sa.Integer, nullable=False)
    type_search = sa.Column(sa.Integer, nullable=False)

    # workflow options below
    correspondence_req = sa.Column(sa.Boolean)
    # indicate whether Mandarin is required in the
    # next stage
    mandarin_req = sa.Column(sa.Boolean)

    # IF they select that correspondence is required,
    # then we want to record the following:
    # TODO: add this to the options in the settings page
    type_correspondence = sa.Column(sa.Integer)
    info_from_correspondence = sa.Column(sa.String)
    info_already_found = sa.Column(sa.String)

class Stage_4(Base_Stage_Task):
    __tablename__ = 'stage_4'

    reviews = sa.Column(sa.Integer, nullable=False)
    date = sa.Column(sa.DateTime, nullable=False)
    chin_inv_file_no = sa.Column(sa.Integer)
    counterpart_file_no = sa.Column(sa.Integer)

    mandarin_req = sa.Column(sa.Boolean)

    # IF they select a new file is created, then we need to
    # record the following:
    pid = sa.Column(sa.Integer)
    legal_name = sa.Column(sa.String)
    linked_iid = sa.Column(sa.Integer)
    nickname_iid = sa.Column(sa.String)
    file_checked_la = sa.Column(sa.Boolean)
