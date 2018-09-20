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

@app.route('/tasks/manage', methods=['GET', 'POST'])
@flog.login_required
def manage_tasks():
    return con.manage_tasks()

@app.route('/tasks/edit/<int:id>', methods=['GET', 'POST'])
@flog.login_required
def edit_task(id):
    return con.edit_task(id)

@app.route('/tasks/accept_task/<int:id>', methods=['GET'])
@flog.login_required
def accept_task(id):
    return con.accept_task(id)

@app.route('/tasks/reject_task/<int:id>', methods=['GET'])
@flog.login_required
def reject_task(id):
    return con.reject_task(id)

@app.route('/transaction/manage', methods=['GET', 'POST'])
@flog.login_required
def manage_transactions():
    return con.manage_transactions()

@app.route('/transaction/<int:id>', methods=['GET', 'POST'])
@flog.login_required
def edit_transaction(id):
    return con.edit_transaction(id)

@app.route('/transaction/create', methods=['GET', 'POST'])
@flog.login_required
def create_transaction():
    return con.create_transaction()

@app.route('/stage1/<int:id>', methods=['GET', 'POST'])
@flog.login_required
def stage1(id):
    return con.stage1(id)

@app.route('/stage2', methods=['GET', 'POST'])
@flog.login_required
def stage2():
    return con.stage2()

@app.route('/stage3', methods=['GET', 'POST'])
@flog.login_required
def stage3():
    return con.stage3()

@app.route('/stage4', methods=['GET', 'POST'])
@flog.login_required
def stage4():
    return con.stage4()

@app.route('/roster', methods=['GET', 'POST'])
@flog.login_required
def roster():
    return con.roster()


# API
# ==========================

# get the name of users based on their ID
@app.route('/search-id/<int:id>', methods=['GET', 'POST'])
@flog.login_required
def search_id(id):
    return con.search_id(id)

# return array of id's based on name
@app.route('/search-username/q=<string:query>', methods=['GET', 'POST'])
@flog.login_required
def search_username(query):
    return con.search_username(query)


# required for login manager
# ===========================
@lm.user_loader
def load_user(user_id):
    user = ml.User.query.get(user_id)
    if user:
        return user
    else:
        return None

# destroy the session iff the app shuts down
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

## testing
