import flask as fl
import database as db
import models as ml
import flask_login as flog
import datetime
from passlib.hash import sha512_crypt
import forms as fm
import flask_wtf as wtf

lm = flog.LoginManager() # initialise the login lib

def index():
    unconfirmed_list = ml.User.query.filter(ml.User.confirmed == False).all()
    return fl.render_template('/index.html', unconfirmed_list=unconfirmed_list)

def login():
    if fl.request.method == 'GET':
        current = datetime.datetime.now()
        if 'logged_in' in fl.session:
            return fl.redirect(fl.url_for('index'))
        return fl.render_template('/login.html', current=current)
    else:
        username = fl.request.form['username']
        pw = fl.request.form['pw']
        # now check this against the database
        user_list = ml.User.query.filter(ml.User.email == username).all()
        if len(user_list) == 1:
            user = user_list[0]
            # check that the password is correct
            if sha512_crypt.verify(pw, user.pw_hashed):
                flog.login_user(user)
                fl.session['logged_in'] = user.id
                if user.admin:
                    fl.session['admin'] = True

                next = fl.request.args.get('next')
                return fl.redirect(fl.url_for('index'))
            else:
                fl.flash("Password incorrect!", "error")
                return fl.render_template('/login.html')
        else:
            fl.flash("Login failed!", "error")
            return fl.render_template('/login.html')

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

        # hash the password
        pw_hashed = sha512_crypt.encrypt(pw_raw)

        # convert to bool
        if lang == '1':
            lang = False
        elif lang == '2':
            lang = True

        # create user object and then commit to db
        new_user = ml.User(fname=fname, lname=lname, email=email, language=lang, pw_hashed=pw_hashed, admin=False)
        db.db_session.add(new_user)
        db.db_session.commit()
        fl.flash('success', 'User created.')
        # take us back to the login page.
        return fl.redirect(fl.url_for('login'))

# confirms an account - either la or analyst can do this
def confirm_account(id):
    user = ml.User.query.get(id)
    if user:
        user.confirmed = True
        db.db_session.commit()
        fl.flash("User confirmed", "success")
    else:
        fl.flash("User doesn't exist", "error")

    return fl.redirect(fl.url_for('index'))

# takes an id and presents an admin with the option to modify any trait of
# another user
def edit_user(id):
    if 'admin' in fl.session:
        user = ml.User.query.get(id)
        if fl.request.method == 'GET':
            if user:
                return fl.render_template('edit-user.html', user=user)
            else:
                return fl.abort(404)
        else:
            # get the form dets
            fname = fl.request.form['fname']
            lname = fl.request.form['lname']
            email = fl.request.form['email']
            lang = fl.request.form['language']
            pw_raw = fl.request.form['pw_raw']
            try:
                admin = fl.request.form['admin']
            except KeyError:
                admin = None

            # encrypt
            pw_hashed = sha512_crypt.encrypt(pw_raw)

            # convert to bool
            if lang == '1':
                lang = False
            elif lang == '2':
                lang = True

            # check whether they are the same as before
            if not fname == "":
                if not fname == user.fname:
                    user.fname = fname
            if not lname == "":
                if not lname == user.lname:
                    user.lname = lname
            if not email == "":
                if not email == user.email:
                    user.email = email
            if not lang == "":
                if not lang == user.language:
                    user.language == lang
            # only run this last part if you're an admin
            if 'admin' in fl.session:
                if not admin == user.admin:
                    if admin == 'on':
                        user.admin = True
                    else:
                        user.admin = False

            if not pw_raw == "":
                if not pw_hashed == user.pw_hashed:
                    user.pw_hashed = pw_hashed


            db.db_session.commit()
            next = fl.request.args.get('next')
            fl.flash(user.fname + "'s details updated", 'success')
            return fl.redirect(fl.url_for('manage'))
    else:
        fl.abort(403)

# if a usa is bein' anoying then del them
def delete_user(id):
    if 'admin' in fl.session:
        # show the user profile for that user
        this_is_the_one = ml.User.query.filter(ml.User.id == id).all()
        if len(this_is_the_one) == 1:
            this_is_the_one = this_is_the_one[0]
            if 'logged_in' in fl.session:
                current_user = fl.session['logged_in']
                if not current_user == this_is_the_one.id:
                    db.db_session.delete(this_is_the_one)
                    db.db_session.commit()
                    fl.flash("Successful deletion of "+this_is_the_one.fname+"!", "success")
                    return fl.redirect(fl.url_for('manage'))
                else:
                    fl.flash("Don't try and delete yourself, you wally", "error")
                    return fl.redirect(fl.url_for('manage'))
            else:
                fl.abort(403)
        else:
            fl.flash("Error! There seems to be more than one of this user")
            return fl.redirect(fl.url_for('index'))

# let an admin manage everyone's profile
def manage_profile():
    if fl.request.method == "GET":
        if "admin" in fl.session:
            # serve the list of people who they can manipulate
            user_list = ml.User.query.filter(ml.User.confirmed).all()
            return fl.render_template('leadanalyst/manage.html', user_list=user_list)
        else:
            #serve them the page that let's them ml their own user Profiles
            # get session user object
            user_id = fl.session['logged_in']
            return fl.redirect(fl.url_for('edit_user', id=user_id))
    else:
        fl.abort(404)

# serve a form and then if it's a POST request we validate and submit
def settings():
    form = fm.Settings_Search(fl.request.form)
    if fl.request.method == 'GET':
        return fl.render_template('settings.html', form=form)

    else:
        if form.validate_on_submit():
            update = ml.Admin()
            new_search_names = ml.Search_Names(name=form.search_name.data)
            update.search_names.append(new_search_names)
            db.db_session.add(update)
            db.db_session.commit()
            fl.flash("Search updated with "+form.search_name.data, "success")
            return fl.render_template('settings.html', form=form)
        else:
            fl.flash("Search not updated", "error")
            return fl.render_template("settings.html", form=form)

# get info about each dataset and then display it to a user
def manage_datasets():
    if fl.request.method == 'GET':
        final = {}
        access_id_num = {}
        all_ds = ml.Dataset.query.all() # get all datasets
        # get all relevant st's
        all_st = ml.Search_Names.query.order_by(ml.Search_Names.id).all()
        # number of entries in the authentication table
        num_access = ml.Dataset_Authd.query.count()
        for i in range(1, num_access+1, 1): # start=1; for each entry in auth
            c = 0
            # start=1; get jth and test against the ds id
            for j in range(1, num_access+1, 1):
                q = ml.Dataset_Authd.query.get(j)
                if q.dataset_id == i:
                     c += 1
            access_id_num[i] = c # add the count to the dictionary at ith entry
        # map id of search type to name
        for ds in all_ds:
            st = ml.Search_Names.query.filter(ml.Search_Names.id == ds.search_type).first()
            final[ds.id] = st.name
        return fl.render_template('leadanalyst/dataset/manage.html', \
        list=all_ds, st=final, access_id_num=access_id_num)
    else:
        fl.abort(404)

# ds creation.
def create_dataset():
    form = fm.Create_Dataset(fl.request.form)
    if fl.request.method == 'GET':
        return fl.render_template('leadanalyst/dataset/create.html', form=form)
    else:
        # process
        if form.validate_on_submit():
            # submit to db
            user = fl.session['logged_in']
            ds = ml.Dataset(name=form.name.data, \
            search_type=int(form.search_type.data), user_created=int(user), \
            year_start=form.year_start.data, year_end=form.year_end.data, \
            owner=user)
            ds_auth_owner = ml.Dataset_Authd(access=user)
            ds_auth = ml.Dataset_Authd(access=form.access.data)
            time_created = datetime.datetime.now()
            ds.time_created = time_created
            ds.access.append(ds_auth)
            ds.access.append(ds_auth_owner)
            db.db_session.add(ds)
            db.db_session.commit()
            fl.flash("Added the dataset!", "success")
            return fl.render_template('leadanalyst/dataset/create.html', form=form)
        else:
            fl.flash("Dataset not created", "error")
            return fl.render_template('leadanalyst/dataset/create.html', form=form)

def edit_dataset(id):
    form = fm.Edit_Dataset(fl.request.form)
    if fl.request.method == 'GET':
        ds = ml.Dataset.query.get(id)
        return fl.render_template('leadanalyst/dataset/edit.html', form=form, ds=ds)
    else:
        # here we need to process the request.
        ds_db = ml.Dataset.query.get(id)

        # get the vars
        name = fl.request.form['name']
        st = fl.request.form['search_type']
        year_start = fl.request.form['year_start']
        year_end = fl.request.form['year_end']
        access = fl.request.form['access']

        if name != "":
            if ds_db.name != name:
                ds_db.name = name
        if st != "":
            if ds_db.search_type != st:
                ds_db.search_type = st

        if year_start != "":
            if ds_db.year_start != year_start:
                ds_db.year_start = year_start

        if year_end != "":
            if ds_db.year_end != year_end:
                ds_db.year_end = year_end

        if access != "":
            if ds_db.access != access:
                ds_auth = ml.Dataset_Authd(access=access)
                ds_db.access.append(ds_auth)

        # send it to db
        db.db_session.commit()
        fl.flash("Updated dataset", "success")
        return fl.redirect(fl.url_for("manage_datasets"))

# delete a ds.
def delete_dataset(id):
    if fl.request.method == 'GET':
        ds = ml.Dataset.query.get(id)
        db.db_session.delete(ds)
        db.db_session.commit()
        return fl.redirect(fl.url_for('manage_datasets'))
    else:
        return fl.redirect(fl.url_for('manage_datasets'))
