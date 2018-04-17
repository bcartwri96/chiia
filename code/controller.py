import flask as fl
import database as db
import models as mod
import flask_login

lm = flask_login.LoginManager() # initialise the login lib

def index():
    return fl.render_template('/index.html')

def login():
    import datetime
    if fl.request.method == 'GET':
        current = datetime.datetime.now()
        # new_user = mod.User()
        # db.db_session.add(new_user)
        # db.db_session.commit()
        # user = mod.User.query.order_by(mod.User.id.desc()).first()
        return fl.render_template('/login.html', current=current)
    else:
        username = fl.request.form['username']
        pw = fl.request.form['pw']
        # now check this against the database
        user_list = mod.User.query.filter(mod.User.email == username)
        if len(user_list) == 1:
            user = user_list[0]
            # user = mod.User()
            # user =
            # user.email = username
            flask_login.login_user(user)

            next = fl.request.args.get('next')
            return fl.render_template('/index.html')
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

        # convert to bool
        if lang == '1':
            lang = False
        elif lang == '2':
            lang = True

        # create user object and then commit to db
        new_user = mod.User(fname=fname, lname=lname, email=email, language=lang)
        db.db_session.add(new_user)
        db.db_session.commit()

        # take us back to the login page.
        return fl.redirect(fl.url_for('login_ret'))
