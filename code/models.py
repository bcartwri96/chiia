import database as db
from flask import Flask
import sqlalchemy as sa
import sqlalchemy.orm as sao
import datetime
from sqlalchemy.ext.declarative import declared_attr
from proj_types import State

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
    avg_time_to_complete = sa.Column(sa.Float, default=2)

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
    freq = sa.Column(sa.Integer, nullable=False)
    # daily = 1; weekly = 2; monthly = 3;
    time_created = sa.Column(sa.DateTime, nullable=False)
    year_start = sa.Column(sa.DateTime, nullable=False)
    year_end = sa.Column(sa.DateTime, nullable=False)
    owner = sa.Column(sa.Integer, nullable=False)
    access = sao.relationship("Dataset_Authd", backref='dataset', lazy=True)

# class maps the dataset access privs to the related ds
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

class Frequencies(db.Base):
    __tablename__ = 'frequencies'
    __table_args__ = {'extend_existing': True}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    days_in_freq = sa.Column(sa.Integer, nullable=False)

# tasks
# ======

class Tasks(db.Base):
    __tablename__ = 'tasks'
    __table_args__ = {'extend_existing' : True}

    id = sa.Column(sa.Integer, primary_key=True)
    nickname = sa.Column(sa.String, nullable=False)
    date_created = sa.Column(sa.DateTime, nullable=False)
    dataset_owner = sa.Column(sa.Integer, nullable=False)
    date_start = sa.Column(sa.DateTime, nullable=False)
    date_end = sa.Column(sa.DateTime, nullable=False)
    date_modified =sa.Column(sa.DateTime, nullable=False)

    # adding these 3 columns as mentioned by document shared by Susan
    # (Stage interior list)
    date_conducted = sa.Column(sa.DateTime)
    total_no_of_result = sa.Column(sa.Integer)
    no_of_result_to_s2 = sa.Column(sa.Integer)


    search_term = sa.Column(sa.String)

    # describes the current state with reference
    # to the transaction id
    stage = sa.Column(sa.Integer, nullable=False)

    who_assigned = sa.Column(sa.Integer, nullable=False)

    trans = sao.relationship("Transactions", backref="Tasks", cascade="all, delete-orphan")
    state = sa.Column(sa.Enum(State), nullable=False)

    # How will state work? It can be three possible points: Pending, Accept,
    # Rejected and Working. It describes the relationship between the LA and the analyst.
    # There are some defined states which let the user in question know whether
    # the LA has seen and accepted their change, whether they have rejected it,
    # whether it is yet to be considered or whether the A is still working on it
    # and therefore has no need for the LA to examine their work. These states
    # can be found in the proj_types.py file.


# How does this transaction thing work?
# Broadly, _if everything goes well_ then we have
# transactions, stage 2, stage 3 and then stage 4
# one single article with a particular search method
# will be the object of all these steps - this means we
# need to track the progress of these stages and how each,
# for instance, transaction will connect to it's stage 2 etc.

# Transactions are technically stage 1 and so we can treat them
# the same as we might treat stage 2, 3 or 4.

# stages
# ======

# base stage class
class Base_Stage_Task(db.Base):
    __table_args__ = {'extend_existing' : True}
    # idea to make abstract credit to:
    # https://mail.python.org/pipermail/flask/2016-February/000261.html
    __abstract__ = True

    # unique identifier for each stage
    s_id = sa.Column(sa.Integer, primary_key=True)
    # speaking of the transaction id, we need to know exactly
    # what the transaction is which we're referring to
    entity_name = sa.Column(sa.String, nullable=False)
    who_assigned = sa.Column(sa.Integer)

# transactions (stage 1)
# =============

class Transactions(Base_Stage_Task):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing' : True}

    amount = sa.Column(sa.Float)
    who_previous_stages = sa.Column(sa.PickleType)

    dataset_id = sa.Column(sa.Integer, nullable=False)
    task_id = sa.Column(sa.Integer)
    # will a transaction have a link to the task?
    # I don't think it needs to, but we'll include
    # it for completeness

    # record the following
    annoucement_date = sa.Column(sa.DateTime)
    rumour_date = sa.Column(sa.DateTime)
    mandarin = sa.Column(sa.Boolean)

    # this is the state of each of the transactions.
    # can be done, need a redo or archived.
    state = sa.Column(sa.Integer, nullable=False)

    tasks = sa.Column(sa.Integer, sa.ForeignKey('tasks.id'))

class Stage_2(Base_Stage_Task):
    __tablename__ = 'stage_2'
    # __table_args__ = {'extend_existing' : True}

    # num times assigned to an analyst
    reviews = sa.Column(sa.Integer)
    # date originally assigned
    date_assigned = sa.Column(sa.DateTime)
    chin_inv_file_no = sa.Column(sa.Float)
    counterpart_file_no = sa.Column(sa.Float)

    # workflow options below
    correspondence_req = sa.Column(sa.Boolean)
    # indicate whether Mandarin is required in the
    # next stage
    mandarin_req = sa.Column(sa.Boolean)
    # if needs to be redone because of a langauge barrier (chinese speaker )
    redo_by_mandarin = sa.Column(sa.Boolean)
    # if needs to be redone because of a langauge barrier (chinese speaker )
    redo_by_non_mandarin = sa.Column(sa.Boolean)
    # IF they select that correspondence is required,
    # then we want to record the following:
    # TODO: add this to the options in the settings page
    type_correspondence = sa.Column(sa.String)
    info_from_correspondence = sa.Column(sa.String)
    info_already_found = sa.Column(sa.String)

    # IF they select a new file is created, then we need to
    # record the following:
    pid = sa.Column(sa.Integer)
    legal_name = sa.Column(sa.String)
    linked_iid = sa.Column(sa.Integer)
    nickname_iid = sa.Column(sa.String)
    file_checked_la = sa.Column(sa.Boolean)

    stage_2_id = sao.relationship("Stage_Rels")

class Stage_3(Base_Stage_Task):
    __tablename__ = 'stage_3'

    reviews = sa.Column(sa.Integer)
    date_assigned = sa.Column(sa.DateTime)
    #type_search = sa.Column(sa.Integer, nullable=False)   # Not required
    dataset_type = sa.Column(sa.String) # Only one of two values  main or supplementary

    # workflow options below
    correspondence_req = sa.Column(sa.Boolean)
    # indicate whether Mandarin is required in the
    # next stage
    mandarin_req = sa.Column(sa.Boolean)
    # if needs to be redone because of a langauge barrier (chinese speaker )
    redo_by_mandarin = sa.Column(sa.Boolean)
    # if needs to be redone because of a langauge barrier (chinese speaker )
    redo_by_non_mandarin = sa.Column(sa.Boolean)
    # IF they select that correspondence is required,
    # then we want to record the following:
    # TODO: add this to the options in the settings page
    type_correspondence = sa.Column(sa.String)
    info_from_correspondence = sa.Column(sa.String)
    info_already_found = sa.Column(sa.String)

    stage_3_id = sao.relationship("Stage_Rels")

class Stage_4(Base_Stage_Task):
    __tablename__ = 'stage_4'

    reviews = sa.Column(sa.Integer)
    date = sa.Column(sa.DateTime)
    chin_inv_file_no = sa.Column(sa.Integer)
    counterpart_file_no = sa.Column(sa.Integer)

    #mandarin_req = sa.Column(sa.Boolean)

    # IF they select a new file is created, then we need to
    # record the following:
    pid = sa.Column(sa.Integer)
    legal_name = sa.Column(sa.String)
    linked_iid = sa.Column(sa.Integer)
    nickname_iid = sa.Column(sa.String)
    file_checked_la = sa.Column(sa.Boolean)

    stage_4_id = sao.relationship("Stage_Rels")

# Establish a table to store the relationships
# between each of the different stages so we can see
# the progression.

class Stage_Rels(db.Base):
    __tablename__ = 'stage_rels'

    trans_id = sa.Column(sa.Integer, sa.ForeignKey('transactions.s_id'), primary_key=True)
    stage_2_id = sa.Column(sa.Integer, sa.ForeignKey('stage_2.s_id'))
    stage_3_id = sa.Column(sa.Integer, sa.ForeignKey('stage_3.s_id'))
    stage_4_id = sa.Column(sa.Integer, sa.ForeignKey('stage_4.s_id'))

    # trans = sao.relationship(Transactions, backref=sao.backref("stage_rels", cascade="all"))
    # tasks = sao.relationship(Tasks, backref=sao.backref("stage_rels", cascade="all"))


class Roster(db.Base):
    __tablename__ = 'roster'
    __table_args__ = {'extend_existing': True}

    user_id = sa.Column(sa.Integer,nullable=False, primary_key=True)
    week_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    no_of_hours = sa.Column(sa.Integer, nullable=False)
    already_allocated = sa.Column(sa.Boolean) #if true, then we've already
    # allocated the users week to maximum hours (i.e so don't do that again!)

class Calendar(db.Base):
    __tablename__ = 'calendar'
    __table_args__ = {'extend_existing': True}

    id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    start_date = sa.Column(sa.DateTime, nullable=False)
    end_date = sa.Column(sa.DateTime, nullable=False)
