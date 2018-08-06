import flask as fl
from flask_sqlalchemy import SQLAlchemy
import os
import controller as con
from database import db_session
import database
import models as ml
import flask_login as flog
import datetime
from flask_bootstrap import Bootstrap


app = fl.Flask(__name__)
lm = flog.LoginManager() # initialise the login lib
lm.init_app(app) # init the login
app.secret_key = database.get_env_variable("SECRET_KEY")  # Change this!
app.permanent_session_lifetime = datetime.timedelta(hours=12)

# main pages
# ==========
# below defines the mapping between URI -> controller code
@app.route('/')
def index():
    return con.index()

@app.route('/index')
def redirect_index():
    return con.index()

# send /login traffic the login page.
@app.route('/login', methods=['GET', 'POST'])
def login():
    return con.login()

@app.route('/create', methods=['GET', 'POST'])
def create():
    return con.create_account()

@app.route('/confirm_account/<int:id>')
@flog.login_required
def confirm_account(id):
    return con.confirm_account(id)

@app.route("/logout")
@flog.login_required
def logout():
    fl.session.clear()
    flog.logout_user()
    return fl.redirect(fl.url_for('index'))

@app.route("/settings", methods=['GET', 'POST'])
@flog.login_required
def settings():
    return con.settings()

# user actions
# ============
@app.route("/manage")
@flog.login_required
def manage():
    return con.manage_profile()

@app.route("/edit-user/<int:id>", methods=['GET', 'POST'])
@flog.login_required
def edit_user(id):
    return con.edit_user(id)

@app.route('/delete-user/<int:id>')
@flog.login_required
def delete_user(id):
    return con.delete_user(id)

# datasets
# ========

@app.route("/dataset/", methods=['GET', 'POST'])
@flog.login_required
def manage_datasets():
    return con.manage_datasets()

@app.route("/dataset/create", methods=['GET', 'POST'])
@flog.login_required
def create_dataset():
    return con.create_dataset()

@app.route("/dataset/edit/<int:id>", methods=['GET', 'POST'])
@flog.login_required
def edit_dataset(id):
    return con.edit_dataset(id)

@app.route("/dataset/delete/<int:id>", methods=['GET', 'POST'])
@flog.login_required
def delete_dataset(id):
    return con.delete_dataset(id)

# Stages
# ========

@app.route('/transaction/manage', methods=['GET', 'POST'])
@flog.login_required
def manage_transactions():
    return con.manage_transactions()

@app.route('/transaction/<int:id>', methods=['GET', 'POST'])
@flog.login_required
def manage_ind_trans(id):
    return con.manage_ind_trans(id)

@app.route('/task/edit/<int:id>', methods=['GET', 'POST'])
@flog.login_required
def edit_task(id):
    return con.edit_task(id)

@app.route('/transaction/create', methods=['GET', 'POST'])
@flog.login_required
def create_transaction():
    return con.create_transaction()

# required for login manager
# ===========================
@lm.user_loader
def load_user(user_id):
    user = ml.User.query.get(user_id)
    if user:
        return user
    else:
        return None

# tear down the session iff the app shuts down
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
