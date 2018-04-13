from flask import Flask as fl
from flask_sqlalchemy import SQLAlchemy
import os
from code import controller as con
from code.database import db_session

app = fl(__name__)
app.debug=True

# below defines the mapping between URI -> controller code
@app.route('/')
def hello_w():
    return "Hello World!"

# send /login traffic the login page.
@app.route('/login')
def login_ret():
    return con.login()


# tear down the session iff the app shuts down
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
