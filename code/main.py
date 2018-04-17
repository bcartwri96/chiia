from flask import Flask as fl
from flask_sqlalchemy import SQLAlchemy
import os
import controller as con
from database import db_session
import models as ml
import flask_login

app = fl(__name__)
lm = flask_login.LoginManager() # initialise the login lib
lm.init_app(app) # init the login
app.secret_key = 'super secret string'  # Change this!

# below defines the mapping between URI -> controller code
@app.route('/')
def index():
    return con.index()

# send /login traffic the login page.
@app.route('/login', methods=['GET', 'POST'])
def login():
    return con.login()

@app.route('/create', methods=['GET', 'POST'])
def create():
    return con.create_account()

@lm.user_loader
def load_user(user_id):
    user = ml.User.query.get(user_id)
    if user:
        return User(user)
    else:
        return None

# tear down the session iff the app shuts down
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
