import flask as fl
import database as db

def login():
    return fl.render_template('/login.html')
