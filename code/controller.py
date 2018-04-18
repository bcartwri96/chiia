import flask as fl
import database as db
import models as mod
import flask_login as flog
import datetime

lm = flog.LoginManager() # initialise the login lib

def index():
    return fl.render_template('/index.html')

def login():
    if fl.request.method == 'GET':
        if 'logged_in' in fl.session:
            return fl.redirect(fl.url_for('index'))
        # user = mod.User.query.order_by(mod.User.id.desc()).first()
        return fl.render_template('/login.html', current=current)
    else:
        username = fl.request.form['username']
        pw = fl.request.form['pw']
        # now check this against the database
        user_list = mod.User.query.filter(mod.User.email == username)
        print(user_list)
        if 1 == 1: #len(user_list) == 1:
            user = user_list[0]
            # user = mod.User()
            # user =
            # user.email = username
            flog.login_user(user)
            fl.session['logged_in'] = True
            next = fl.request.args.get('next')
            return fl.redirect(fl.url_for('index'))
        else:
            fl.flash("Login failed")
            return fl.render_template(fl.url_for('login'))
def create_account():
    if fl.request.method == 'GET':
        return fl.render_template('create_account.html')
    else:
        #get form data
        fname = fl.request.form['fname']
        lname = fl.request.form['lname']
        email = fl.request.form['email']
        lang = fl.request.form['language']
        pw_raw = fl.request.form['pw_raw']

        # convert to bool
        if lang == '1':
            lang = False
        elif lang == '2':
            lang = True

        # create user object and then commit to db
        new_user = mod.User(fname=fname, lname=lname, email=email, language=lang, pw_hashed=pw_raw)
        db.db_session.add(new_user)
        db.db_session.commit()

        # take us back to the login page.
        return fl.redirect(fl.url_for('login'))
