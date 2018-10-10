import flask as fl
import database as db
import models as ml
import flask_login as flog
import datetime as dt
from passlib.hash import sha512_crypt
from proj_types import State
import flask_wtf as wtf
import sqlalchemy as sa
import json as js
import send as s

lm = flog.LoginManager() # initialise the login lib

def index():
    unconfirmed_list = ml.User.query.filter(ml.User.confirmed == False).all()
    return fl.render_template('/index.html', unconfirmed_list=unconfirmed_list)

def login():
    if fl.request.method == 'GET':
        current = dt.datetime.now()
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
                if user.confirmed:
                    flog.login_user(user)
                    fl.session['logged_in'] = user.id
                    if user.admin:
                        fl.session['admin'] = True

                    next = fl.request.args.get('next')
                    return fl.redirect(fl.url_for('index', next=next))
                else:
                    fl.flash("Account not confirmed yet! Wait for confirmation",
                    "error")
                    return fl.render_template('/login.html')
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
                    user.language = lang
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
    elif 'admin' not in fl.session:
        user = ml.User.query.get(id)
        if fl.request.method == 'GET':
            if id == fl.session['logged_in']:
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
                    user.language = lang

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
    import forms as fm
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
def create_dataset(**kwargs):
    from sqlalchemy import func, asc
    import forms as fm
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
            owner=user, freq=int(form.freq.data))
            ds_auth_owner = ml.Dataset_Authd(access=user)
            ds_auth = ml.Dataset_Authd(access=form.access.data)
            time_created = dt.datetime.now()
            ds.time_created = time_created
            ds.access.append(ds_auth)
            ds.access.append(ds_auth_owner)
            db.db_session.add(ds)
            db.db_session.commit()
            fl.flash("Added the dataset!", "success")
            # now break up this into the correct amount of tasks
            freq_list, start, end = get_time_list(form.year_start.data, \
            form.year_end.data, form.freq.data)
            ds_id = ml.Dataset.query.order_by(sa.desc(ml.Dataset.id)).first()
            if ds_id == None:
                ds_id = 1
            else:
                ds_id = ds_id.id
            for i in range(0, len(freq_list), 1):
                # create a task for every frequency object

                t_cur = ml.Tasks()
                t_cur.nickname = freq_list[i]
                t_cur.date_created = dt.datetime.now()
                t_cur.dataset_owner = int(ds_id)
                t_cur.date_start = start[i]
                t_cur.date_end = end[i]
                t_cur.who_assigned = int(user)
                t_cur.num_inv_found = 0
                t_cur.num_inv_progressing = 0
                t_cur.date_modified = dt.datetime.now()

                db.db_session.add(t_cur)

            db.db_session.commit()
            return fl.render_template('leadanalyst/dataset/create.html', form=form)
        else:
            # return str(form.freq.data)
            fl.flash("Dataset not created", "error")
            fl.flash(str(form.errors), 'error')
            return fl.render_template('leadanalyst/dataset/create.html', form=form)


def get_time_list(initial, end, interval):
    """the purpose of this function is to calculate the amount and at what
    intervals they should occur."""
    import datetime as dt
    # ensure data is actually legit
    try:
        initial = dt.datetime.strptime(initial, "%Y-%m-%d %H:%M:%S")
        end = dt.datetime.strptime(end,  "%Y-%m-%d %H:%M:%S")
    except ValueError:
        fl.flask("Internal Server Error", "error")
        return None
    except TypeError:
        pass
    # time delta indicates the period we need to calculate over
    time_delta = end-initial
    # now divide this between the interval
    int = dt.timedelta(days = interval)
    # now create and return a list of each interval
    name = []
    start_date = []
    end_date = []
    for i in range(0, round(time_delta.days/int.days), 7):
        t_start = initial + dt.timedelta(i*int.days)
        t_end = t_start + dt.timedelta(7 - 1)
        start_date.append(t_start)
        end_date.append(t_end)
        name.append(dt.datetime.strftime(t_start, "%d-%m-%y") + "->" + dt.datetime.strftime(t_end, "%d-%m-%y"))
    return name, start_date, end_date


def edit_dataset(id):
    import forms as fm
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

def edit_task(id):
    """take a task id and allow the user to edit who all the properties of
    a task."""
    import forms as fm
    form = fm.Edit_Task(fl.request.form)
    new_transaction = fm.Create_Transaction(fl.request.form)
    t_db = ml.Tasks.query.get(id)
    all_trans = t_db.trans
    if fl.request.method == 'GET':
        u = ml.User.query.get(int(t_db.who_assigned))
        form.nickname.data = t_db.nickname
        form.date_start.data = t_db.date_start
        form.date_end.data = t_db.date_end
        # form.search_term.data = t_db.search_term
        form.who_assigned.data = u.fname + " "+ u.lname
        form.dataset_owner.data = t_db.dataset_owner
        form.who_assigned_real.data = t_db.who_assigned

        # get all the related transactions to this task
        return fl.render_template('leadanalyst/task/edit.html', form=form, t=t_db,
        trans=new_transaction, related_trans=all_trans)

    else:
        # process form/s

        # RECALL: transactions are many-to-one so for every stage_rel id, we
        # can have multiple id's related to transactions and this means we will
        # be CREATING a new transaction here!
        if form.validate_on_submit() and form.task_submitted.data:
            #get the vars
            nickname = fl.request.form['nickname']
            date_start = fl.request.form['date_start']
            date_end = fl.request.form['date_end']
            who_assigned = fl.request.form['who_assigned_real']

            t_db.nickname = nickname
            t_db.date_start = date_start
            t_db.date_end = date_end
            t_db.who_assigned = who_assigned
            # t_db.search_term = search_term
            t_db.date_modified = dt.datetime.now()

            db.db_session.add(t_db)
            try:
                db.db_session.commit()
                fl.flash("Updated task", "success")
            except sa.exc.InvalidRequestError():
                fl.flash("Failed to update task", "failed")

        elif new_transaction.validate_on_submit() and \
        new_transaction.trans_submitted.data:
                # process the new transaction here and ensure it is bound
                # to the stage_rels table mapping.

                trans = ml.Transactions()
                # get vars from transaction/s
                t_name = fl.request.form['entity_name']
                t_rumour_date = fl.request.form['rumour_date']
                t_announcement_date = fl.request.form['anouncement_date']
                # get the max id and then increment
                max_id = db.db_session.query(sa.func.max(ml.Transactions.s_id)).scalar()
                if not max_id == None:
                    # initially, none in db so NoneType returned
                    trans.id = max_id+1
                else:
                    trans.id = 1

                trans.entity_name = t_name
                trans.rumour_date = t_rumour_date
                trans.annoucement_date = t_announcement_date

                # update relations
                # create a stage_rel mapping between the trans and the task
                t_db.trans.append(trans)

                # now relate the stage rel to the task (which definitely exists
                # because we're editing it!)
                # stage_rel.tasks_id = id
                # t_db.task_id.append(stage_rel)

                # submit this
                #trans.amount = 100
                trans.dataset_id = 1

                # recall that changing a transaction means modifying the task,
                # so change the task too.
                t_db.date_modified = dt.datetime.now()
                fl.flash("date adjusted to "+str(dt.datetime.now()), 'success')

                db.db_session.add(trans)
                db.db_session.add(t_db)
                # db.db_session.add(stage_rel)

                try:
                    db.db_session.commit()
                    fl.flash("Bound new transaction to current task "+str(t_db.nickname), 'success')
                except sa.exc.InvalidRequestError():
                    fl.flash("Failed to create transaction", "failed")

        else:
            fl.flash("Failed to update", "error")
            fl.flash(str(form.errors), 'error')
            fl.flash(str(new_transaction.errors), 'error')

        return fl.render_template('leadanalyst/task/edit.html', form=form, t=t_db,
        trans=new_transaction, related_trans=all_trans)

# accepting a task at the current stage involves moving it to the next
# stage and it also involves notifying the person responsible for it
def accept_task(id):
    cur_task = ml.Tasks.query.get(id)

    # now take task and increment the stage
    cur_task.stage = cur_task.stage + 1
    # now update the state
    cur_task.state = State.Accepted

    db.db_session.add(cur_task)
    db.db_session.commit()
    return fl.redirect(fl.url_for("manage_tasks"))

# same but for rejection
def reject_task(id):
    cur_task = ml.Tasks.query.get(id)

    # change the state to rejected but then don't do anything
    cur_task.state = State.Rejected

    db.db_session.add(cur_task)
    db.db_session.commit()
    return fl.redirect(fl.url_for('manage_tasks'))

# delete a ds.s
def delete_dataset(id):
    if fl.request.method == 'GET':
        ds = ml.Dataset.query.get(id)
        task = ml.Tasks.query.filter_by(dataset_owner=ds.id).all()
        for tl in task:
            tran = ml.Transactions.query.filter_by(tasks=tl.id).all()
            for tr in tran:
                sr = ml.Stage_Rels.query.filter_by(trans_id=tr.s_id).first()
                s2 = ml.Stage_2.query.filter_by(s_id = sr.stage_2_id).first()
                s3 = ml.Stage_3.query.filter_by(s_id = sr.stage_3_id).first()
                s4 = ml.Stage_4.query.filter_by(s_id = sr.stage_4_id).first()
                db.db_session.delete(sr)
                db.db_session.commit()
                if s4 != None:
                    db.db_session.delete(s4)
                if s3 != None:
                    db.db_session.delete(s3)
                if s2 != None:
                    db.db_session.delete(s2)
                #db.db_session.delete(s3)
                #db.db_session.delete(s2)
                db.db_session.delete(tr)
            db.db_session.delete(tl)
        db.db_session.delete(ds)
        db.db_session.commit()
        return fl.redirect(fl.url_for('manage_datasets'))
    else:
        return fl.redirect(fl.url_for('manage_datasets'))


def manage_tasks():
    """This will present the page which let's LA see all current transactions"""
    if fl.request.method == 'GET':
        if 'admin' not in fl.session:
            current_user = fl.session['logged_in']
            # not LA, so only get tasks allocated to them
            t = ml.Tasks.query.filter(ml.Tasks.who_assigned == current_user).all()
            s2 = ml.Stage_2.query.filter(ml.Stage_2.who_assigned == current_user).all()
            s3 = ml.Stage_3.query.filter(ml.Stage_3.who_assigned == current_user).all()
            s4 = ml.Stage_4.query.filter(ml.Stage_4.who_assigned == current_user).all()

            return fl.render_template('analyst/manage_task.html', tasks=t,stage2=s2,stage3=s3,stage4=s4)
        elif fl.session['admin']:
            t = ml.Tasks.query.all()
            # get weeks
            weeks = weekCalc(t)

            # get recent, too
            d = dt.datetime.now() - dt.timedelta(days=1)
            rec = ml.Tasks.query.filter(ml.Tasks.date_modified >= d).order_by(sa.desc(ml.Tasks.date_modified)).limit(15).all()
            rec_weeks = weekCalc(rec)

            return fl.render_template('leadanalyst/task/manage.html',
            all=zip(t,weeks), recent=zip(rec, rec_weeks))


def weekCalc(tasks):
    weeks = []
    # perform week calculation
    for cur in tasks:
        ds = cur.date_start
        de = cur.date_end
        time_delta = de-ds
        # time_delta = time_delta(days=time_delta)
        weeks.append(time_delta)
    return weeks

# get all transactions if admin and get all transactions
# relevant to an analyst
def manage_transactions():
    if fl.request.method == 'GET':
        if fl.session['admin']:
            # query the db and fetch all
            # current transactions
            trans = ml.Transactions.query.all()
            tasks = ml.Tasks.query.all()
            return fl.render_template('manage_transactions.html', trans=trans,\
            tasks=tasks)
        else:
            fl.abort(404)
    else:
        fl.abort(404)

def edit_transaction(id):
    trans = ml.Transactions.query.filter(ml.Transactions.s_id == id).all()[0]
    if trans:
        return fl.render_template('edit_transaction.html', t=trans)
    else:
        fl.abort(404)

def create_transaction():
    import forms as fm
    # get the current user's id and then submit that
    form = fm.Create_Transaction(fl.request.form)
    if fl.request.method == 'GET':
        return fl.render_template('create_trans.html', form=form)
    else:
        # other auto vars to be stored
        # dataset_id =
        pass

def stage1(id):
    import forms as fm
    # just defining get method as of now. Need to work on post and predefined columns
    #  after task assignment part is completed
    # Also need to add add_transaction part here
    import datetime as dt
    form = fm.stage1(fl.request.form)
    new_transaction = fm.Create_Transaction(fl.request.form)
    t_db = ml.Tasks.query.get(id)
    all_trans = t_db.trans
    if fl.request.method == 'GET':
        uid = t_db.who_assigned
        user = ml.User.query.filter_by(id=uid ).first()
        user_name = user.fname +" "+ user.lname
        form.who_assigned.data = user_name
        form.date_conducted.data = dt.datetime.now()
        form.date_start.data = t_db.date_start
        form.date_end.data = t_db.date_end

        # get all the related transactions to this task
        return fl.render_template('analyst/stage1.html', form=form, t=t_db, \
        trans=new_transaction, related_trans=all_trans)

    else:
        # process form/s

        # RECALL: transactions are many-to-one so for every stage_rel id, we
        # can have multiple id's related to transactions and this means we will
        # be CREATING a new transaction here!
        if form.validate_on_submit() and form.task_submitted.data:
            #get the vars
            #who_assigned = fl.request.form['who_assigned']
            search_term = fl.request.form['search_term']
            date_start = fl.request.form['date_start']
            date_end = fl.request.form['date_end']
            date_conducted = fl.request.form['date_conducted']
            total_no_of_result = fl.request.form['total_no_of_result']
            #who_assigned = fl.request.form['who_assigned']

            #t_db.who_assigned = who_assigned
            t_db.date_start = date_start
            t_db.date_end = date_end
            #t_db.who_assigned = who_assigned
            t_db.search_term = search_term

            #t_db.date_modified = dt.datetime.now()
            t_db.date_conducted = date_conducted
            t_db.total_no_of_result = total_no_of_result

            db.db_session.add(t_db)
            try:
                db.db_session.commit()
                fl.flash("Updated task", "success")
            except sa.exc.InvalidRequestError():
                fl.flash("Failed to update task", "error")


        elif new_transaction.validate_on_submit() and \
        new_transaction.trans_submitted.data:
                # process the new transaction here and ensure it is bound
                # to the stage_rels table mapping.

                trans = ml.Transactions()
                # get vars from transaction/s
                t_name = fl.request.form['entity_name']
                t_rumour_date = fl.request.form['rumour_date']
                t_announcement_date = fl.request.form['anouncement_date']
                try:
                    mandarin_req = fl.request.form['mandarin_req']
                except KeyError:
                    mandarin_req = None
                if mandarin_req == 'on':
                    mandarin_req = True
                else:
                    mandarin_req = False

                # get the max id and then increment
                max_id = db.db_session.query(sa.func.max(ml.Transactions.s_id)).scalar()
                if not max_id == None:
                    # initially, none in db so NoneType returned
                    trans.id = max_id + 1
                else:
                    trans.id = 1

                trans.entity_name = t_name
                trans.rumour_date = t_rumour_date
                trans.annoucement_date = t_announcement_date
                trans.stage = 1
                trans.mandarin_req = mandarin_req
                # update relations
                # create a stage_rel mapping between the trans and the task
                t_db.trans.append(trans)

                # submit this
                #trans.amount = 100
                trans.dataset_id = 1


                # recall that changing a transaction means modifying the task,
                # so change the task too.
                t_db.date_modified = dt.datetime.now()
                fl.flash("date adjusted to "+str(dt.datetime.now()), 'success')

                db.db_session.add(trans)
                db.db_session.add(t_db)
                db.db_session.commit()
                # new transaction means add 1 to the no_progressed to stg2 var in
                # tasks
                if t_db.no_of_result_to_s2 != None:
                    t_db.no_of_result_to_s2 = t_db.no_of_result_to_s2+1
                else:
                    t_db.no_of_result_to_s2 = 1

                # clean up db
                db.db_session.add(t_db)

                try:
                    db.db_session.commit()
                    fl.flash("Bound new transaction to current task "+str(t_db.nickname), 'success')

                    # transition into stage 2
                    s2 = transition_transaction(trans)
                    # NOTE : Do we really need this as this wont allow us to add more transaction
                    #if s2: # if we created the s2 correctly
                        #return fl.redirect(fl.url_for('stage2', s_id=s2.s_id))

                except sa.exc.InvalidRequestError:
                    fl.flash("Failed to create transaction", "error")

        else:
            fl.flash("Failed to update", "error")
            fl.flash(str(form.errors), 'error')
            fl.flash(str(new_transaction.errors), 'error')

        return fl.render_template('analyst/stage1.html', form=form, t=t_db,
        trans=new_transaction, related_trans=all_trans)



def stage2(s_id):
    import forms as fm
    # just defining get method as of now. Need to work on post and predefined columns
    #  after task assignment part is completed
    # Also need to add workflow option as soon as new user is defined
    form = fm.stage2(fl.request.form)
    new_chinese_file  = fm.chinese_investor_file(fl.request.form)
    new_counter_file  = fm.counterpart_investor_file(fl.request.form)
    t_db = ml.Stage_2.query.get(s_id)
    trans = ml.Stage_Rels.query.filter_by(stage_2_id = s_id).first()
    new_counter_file_tb = ml.Counterpart_Investor_File.query.filter_by(linked_iid = trans.trans_id, stage_added = 2).all()
    new_chinese_file_tb = ml.Chinese_Investor_File.query.filter_by(linked_iid = trans.trans_id, stage_added = 2).all()


    import datetime as dt

    if fl.request.method == 'GET':
        form.S2_date.data = dt.datetime.now()
        if not t_db.reviews == None:
            # initially, none in db so NoneType returned
            form.S2_reviews.data = t_db.reviews + 1
        else:
            form.S2_reviews.data = 0
        # get method for adding nnew chinese investor file
        # getting the related IID(trans_id) from stage_rels
        s = ml.Stage_Rels.query.filter_by(stage_2_id=s_id ).first()
        # getting the related entity name from transactions
        sr = ml.Transactions.query.get(s.trans_id)

        new_chinese_file.linked_iid.data = s.trans_id
        new_chinese_file.nickname_iid.data = sr.entity_name


        # get method for adding nnew counterpart investor file
        # getting the related IID(trans_id) from stage_rels

        new_counter_file.counter_linked_iid.data = s.trans_id
        new_counter_file.counter_nickname_iid.data = sr.entity_name
        return fl.render_template('analyst/stage2.html', form=form,t=t_db, \
        new_chinese_file=new_chinese_file,new_counter_file = new_counter_file, \
        new_counter_file_tb= new_counter_file_tb , new_chinese_file_tb = new_chinese_file_tb)
    else:
        if form.validate_on_submit() and form.task_submitted.data:
            # getting details of stage 2

            assigned_date = fl.request.form['S2_date']
            no_of_reviews = int(fl.request.form['S2_reviews'])
            chin_inv_file_no = fl.request.form['chin_inv_file_no']
            counterpart_file_no =  fl.request.form['counterpart_file_no']

            # Correspondence  workflow option
            # correspondence required
            try:
                correspondence_req = fl.request.form['correspondence_req']
            except KeyError:
                correspondence_req = None
            if correspondence_req == 'on':
                correspondence_req = True
            else:
                correspondence_req = False
            try:
                type_correspondence = fl.request.form['type_correspondence']
            except KeyError:
                type_correspondence = None
            if type_correspondence == '1':
                type_correspondence = 'Primary Source'
            elif type_correspondence == '2':
                type_correspondence = 'ASIC Report'
            elif type_correspondence == '3':
                type_correspondence = 'Property Record'
            else:
                type_correspondence = ''
            info_from_correspondence =  fl.request.form['info_from_correspondence']
            info_already_found =  fl.request.form['info_already_found']



            # Next Analyst should be chinese speaker
            try:
                mandarin_req = fl.request.form['mandarin_req']
            except KeyError:
                mandarin_req = None
            if mandarin_req == 'on':
                mandarin_req = True
            else:
                mandarin_req = False

            #Redo this stage with chinese speaker

            try:
                redo_by_mandarin = fl.request.form['redo_by_mandarin']
            except KeyError:
                redo_by_mandarin = None
            if redo_by_mandarin == 'on':
                redo_by_mandarin = True
            else:
                redo_by_mandarin = False
            #Redo this stage without chinese speaker

            try:
                redo_by_non_mandarin = fl.request.form['redo_by_non_mandarin']
            except KeyError:
                redo_by_non_mandarin = None
            if redo_by_non_mandarin == 'on':
                redo_by_non_mandarin = True
            else:
                redo_by_non_mandarin = False

            t_db.reviews = no_of_reviews
            t_db.date_assigned = assigned_date
            t_db.chin_inv_file_no = chin_inv_file_no
            t_db.counterpart_file_no = counterpart_file_no
            t_db.redo_by_mandarin = redo_by_mandarin
            t_db.mandarin_req = mandarin_req
            t_db.redo_by_non_mandarin = redo_by_non_mandarin
            t_db.correspondence_req = correspondence_req
            t_db.type_correspondence = type_correspondence
            t_db.info_from_correspondence = info_from_correspondence
            t_db.info_already_found = info_already_found
            db.db_session.add(t_db)

            # we want to add the transition to s3
            s3 = transition_transaction(t_db)
            if s3 == -1:
                fl.flash("Something", "error")
            # recall: returns the next stage if successful
            try:
                db.db_session.commit()
                fl.flash("Updated stage2", "success")
            except sa.exc.InvalidRequestError():
                fl.flash("Failed to update stage2", "error")
        elif new_counter_file.validate_on_submit() and new_counter_file.counter_file_submitted.data:
            counter_file = ml.Counterpart_Investor_File()
            # getting details of new chinese file investor
            # get the max id and then increment
            max_id = db.db_session.query(sa.func.max(ml.Counterpart_Investor_File.pid)).scalar()
            if not max_id == None:
                # initially, none in db so NoneType returned
                pid = max_id + 1
            else:
                pid = int(1)
            legal_name = fl.request.form['counter_legal_name']
            linked_iid = fl.request.form['counter_linked_iid']
            nickname_iid = fl.request.form['counter_nickname_iid']
            stage_added = 2
            try:
                file_checked_la = fl.request.form['counter_file_checked_la']
            except KeyError:
                file_checked_la = None
            if file_checked_la == 'on':
                file_checked_la = True
            else:
                file_checked_la = False
            counter_file.pid = pid
            counter_file.legal_name = legal_name
            counter_file.linked_iid = linked_iid
            counter_file.nickname_iid = nickname_iid
            counter_file.stage_added = stage_added
            counter_file.file_checked_la = file_checked_la
            db.db_session.add(counter_file)
            fl.flash("create new counterpart investor file", "success")
            try:
                db.db_session.commit()
                fl.flash("create new counterpart investor file", "success")
            except sa.exc.InvalidRequestError:
                fl.flash("Failed to create new counterpart investor file", "error")
        elif new_chinese_file.validate_on_submit() and new_chinese_file.file_submitted.data:
            chinese_file = ml.Chinese_Investor_File()
            # getting details of new counterpart file investor
            # get the max id and then increment
            max_id = db.db_session.query(sa.func.max(ml.Chinese_Investor_File.pid)).scalar()
            if not max_id == None:
                # initially, none in db so NoneType returned
                pid = max_id + 1
            else:
                pid = int(1)
            legal_name = fl.request.form['legal_name']
            linked_iid = fl.request.form['linked_iid']
            nickname_iid = fl.request.form['nickname_iid']
            stage_added = 2
            try:
                file_checked_la = fl.request.form['file_checked_la']
            except KeyError:
                file_checked_la = None
            if file_checked_la == 'on':
                file_checked_la = True
            else:
                file_checked_la = False
            chinese_file.pid = pid
            chinese_file.legal_name = legal_name
            chinese_file.linked_iid = linked_iid
            chinese_file.nickname_iid = nickname_iid
            chinese_file.stage_added = stage_added
            chinese_file.file_checked_la = file_checked_la
            db.db_session.add(chinese_file)
            try:
                db.db_session.commit()
                fl.flash("create new chinese investor file", "success")
            except sa.exc.InvalidRequestError:
                fl.flash("Failed to new chinese investor file", "error")

        else:
            fl.flash("Failed to update", "error")
            fl.flash(str(form.errors), 'error')
            fl.flash(str(new_chinese_file.errors), 'error')
            # fl.flash(str(counter_file.errors), 'error')
        return fl.render_template('analyst/stage2.html', form=form,t=t_db, \
        new_chinese_file= new_chinese_file,new_counter_file = new_counter_file, \
        new_counter_file_tb= new_counter_file_tb, new_chinese_file_tb= new_chinese_file_tb)



def stage3(s_id):
    import forms as fm
    form = fm.stage3(fl.request.form)
    t_db = ml.Stage_3.query.get(s_id)
    import datetime as dt
    if fl.request.method == 'GET':
        form.S3_date.data = dt.datetime.now()
        if not t_db.reviews == None:
            # initially, none in db so NoneType returned
            form.S3_reviews.data = t_db.reviews + 1
        else:
            form.S3_reviews.data = 0
        return fl.render_template('analyst/stage3.html', form=form,t=t_db)
    else:
        assigned_date = fl.request.form['S3_date']
        no_of_reviews = fl.request.form['S3_reviews']

        try:
            dataset_type = fl.request.form['dataset_type']
        except KeyError:
            dataset_type = None
        if dataset_type == '1':
            dataset_type = 'Main'
        elif dataset_type == '2':
            dataset_type = 'Supplementary'
        else:
            type_correspondence = ''

        # Correspondence  workflow option
        try:
            correspondence_req = fl.request.form['correspondence_req']
        except KeyError:
            correspondence_req = None
        if correspondence_req == 'on':
            correspondence_req = True
        else:
            correspondence_req = False
        try:
            type_correspondence = fl.request.form['type_correspondence']
        except KeyError:
            type_correspondence = None
        if type_correspondence == '1':
            type_correspondence = 'Primary Source'
        elif type_correspondence == '2':
            type_correspondence = 'ASIC Report'
        elif type_correspondence == '3':
            type_correspondence = 'Property Record'
        else:
            type_correspondence = ''
        info_from_correspondence =  fl.request.form['info_from_correspondence']
        info_already_found =  fl.request.form['info_already_found']
        # Next Analyst should be chinese speaker
        try:
            mandarin_req = fl.request.form['mandarin_req']
        except KeyError:
            mandarin_req = None
        if mandarin_req == 'on':
            mandarin_req = True
        else:
            mandarin_req = False

        #Redo this stage with chinese speaker

        try:
            redo_by_mandarin = fl.request.form['redo_by_mandarin']
        except KeyError:
            redo_by_mandarin = None
        if redo_by_mandarin == 'on':
            redo_by_mandarin = True
        else:
            redo_by_mandarin = False
        #Redo this stage without chinese speaker

        try:
            redo_by_non_mandarin = fl.request.form['redo_by_non_mandarin']
        except KeyError:
            redo_by_non_mandarin = None
        if redo_by_non_mandarin == 'on':
            redo_by_non_mandarin = True
        else:
            redo_by_non_mandarin = False

        t_db.reviews = no_of_reviews
        t_db.date_assigned = assigned_date
        t_db.dataset_type = dataset_type
        t_db.redo_by_mandarin = redo_by_mandarin
        t_db.mandarin_req = mandarin_req
        t_db.redo_by_non_mandarin = redo_by_non_mandarin
        t_db.correspondence_req = correspondence_req
        t_db.type_correspondence = type_correspondence
        t_db.info_from_correspondence = info_from_correspondence
        t_db.info_already_found = info_already_found


        s4 = transition_transaction(t_db)
        if not s4 == -1:
            fl.flash("Created stage 4 successfully", "success")

        # create complimentry stage2
        # get current max id
        # s4_max = db.db_session.query(sa.func.max(ml.Stage_4.s_id)).scalar()
        # if s4_max:
        #     s4_max+=1
        # else:
        #     s4_max=1
        #
        # s4 = ml.Stage_4(s_id=s4_max)
        # # NOTE: Need to check whether entity name is required in stage 4
        # db.db_session.add(s4)
        #
        # s = ml.Stage_Rels.query.filter_by(stage_3_id=s_id ).first()
        #
        # # now join it to the sr table with the new trans
        # sr = ml.Stage_Rels.query.get(s.trans_id)
        # sr.stage_4_id = s4_max
        #
        db.db_session.add(t_db)
        # db.db_session.add(sr)
        db.db_session.commit()
        fl.flash("Updated stage3", "success")
        return fl.render_template('analyst/stage3.html', form=form,t=t_db)


def stage4(s_id):
    import forms as fm
    form = fm.stage4(fl.request.form)
    new_chinese_file  = fm.chinese_investor_file(fl.request.form)
    new_counter_file  = fm.counterpart_investor_file(fl.request.form)
    t_db = ml.Stage_4.query.get(s_id)
    trans = ml.Stage_Rels.query.filter_by(stage_4_id = s_id).first()
    new_counter_file_tb = ml.Counterpart_Investor_File.query.filter_by(linked_iid = trans.trans_id, stage_added = 4).all()
    new_chinese_file_tb = ml.Chinese_Investor_File.query.filter_by(linked_iid = trans.trans_id, stage_added = 4).all()
    import datetime as dt

    if fl.request.method == 'GET':
        form.S4_date.data = dt.datetime.now()
        if not t_db.reviews == None:
            # initially, none in db so NoneType returned
            form.S4_reviews.data = t_db.reviews + 1
        else:
            form.S4_reviews.data = 0
        # get method for adding nnew chinese investor file
        # getting the related IID(trans_id) from stage_rels
        s = ml.Stage_Rels.query.filter_by(stage_4_id=s_id ).first()
        # getting the related entity name from transactions
        sr = ml.Transactions.query.get(s.trans_id)

        new_chinese_file.linked_iid.data = s.trans_id
        new_chinese_file.nickname_iid.data = sr.entity_name

        # get method for adding nnew counterpart investor file
        # getting the related IID(trans_id) from stage_rels

        new_counter_file.counter_linked_iid.data = s.trans_id
        new_counter_file.counter_nickname_iid.data = sr.entity_name
        return fl.render_template('analyst/stage4.html', form=form, t=t_db,\
        new_chinese_file= new_chinese_file,new_counter_file = new_counter_file, \
        new_counter_file_tb= new_counter_file_tb, new_chinese_file_tb= new_chinese_file_tb)
    else:
        if form.validate_on_submit() and form.task_submitted.data:
            assigned_date = fl.request.form['S4_date']
            no_of_reviews = int(fl.request.form['S4_reviews'])
            chin_inv_file_no = fl.request.form['chin_inv_file_no']
            counterpart_file_no =  fl.request.form['counterpart_file_no']

            try:
                redo_by_mandarin = fl.request.form['redo_by_mandarin']
            except KeyError:
                redo_by_mandarin = None
            if redo_by_mandarin == 'on':
                redo_by_mandarin = True
            else:
                redo_by_mandarin = False
            #Redo this stage without chinese speaker

            try:
                redo_by_non_mandarin = fl.request.form['redo_by_non_mandarin']
            except KeyError:
                redo_by_non_mandarin = None
            if redo_by_non_mandarin == 'on':
                redo_by_non_mandarin = True
            else:
                redo_by_non_mandarin = False

            t_db.reviews = no_of_reviews
            t_db.date = assigned_date
            t_db.chin_inv_file_no = chin_inv_file_no
            t_db.counterpart_file_no = counterpart_file_no
            t_db.redo_by_mandarin = redo_by_mandarin
            t_db.redo_by_non_mandarin = redo_by_non_mandarin
            db.db_session.add(t_db)

            state = transition_transaction(t_db)
            try:
                db.db_session.commit()
                fl.flash("Updated stage4", "success")
            except sa.exc.InvalidRequestError():
                fl.flash("Failed to update stage2", "error")
        elif new_counter_file.validate_on_submit() and new_counter_file.counter_file_submitted.data:
            counter_file = ml.Counterpart_Investor_File()
            # getting details of new chinese file investor
            # get the max id and then increment
            max_id = db.db_session.query(sa.func.max(ml.Counterpart_Investor_File.pid)).scalar()
            if not max_id == None:
                # initially, none in db so NoneType returned
                pid = max_id + 1
            else:
                pid = int(1)
            legal_name = fl.request.form['counter_legal_name']
            linked_iid = fl.request.form['counter_linked_iid']
            nickname_iid = fl.request.form['counter_nickname_iid']
            stage_added = 4
            try:
                file_checked_la = fl.request.form['counter_file_checked_la']
            except KeyError:
                file_checked_la = None
            if file_checked_la == 'on':
                file_checked_la = True
            else:
                file_checked_la = False
            counter_file.pid = pid
            counter_file.legal_name = legal_name
            counter_file.linked_iid = linked_iid
            counter_file.nickname_iid = nickname_iid
            counter_file.stage_added = stage_added
            counter_file.file_checked_la = file_checked_la
            db.db_session.add(counter_file)
            db.db_session.commit()
            fl.flash("create new counterpart investor file", "success")
        elif new_chinese_file.validate_on_submit() and new_chinese_file.file_submitted.data:
            chinese_file = ml.Chinese_Investor_File()
            # getting details of new counterpart file investor
            # get the max id and then increment
            max_id = db.db_session.query(sa.func.max(ml.Chinese_Investor_File.pid)).scalar()
            if not max_id == None:
                # initially, none in db so NoneType returned
                pid = max_id + 1
            else:
                pid = int(1)
            legal_name = fl.request.form['legal_name']
            linked_iid = fl.request.form['linked_iid']
            nickname_iid = fl.request.form['nickname_iid']
            stage_added = 4
            try:
                file_checked_la = fl.request.form['file_checked_la']
            except KeyError:
                file_checked_la = None
            if file_checked_la == 'on':
                file_checked_la = True
            else:
                file_checked_la = False
            chinese_file.pid = pid
            chinese_file.legal_name = legal_name
            chinese_file.linked_iid = linked_iid
            chinese_file.nickname_iid = nickname_iid
            chinese_file.stage_added = stage_added
            chinese_file.file_checked_la = file_checked_la
            db.db_session.add(chinese_file)
            db.db_session.commit()
            fl.flash("create new chinese investor file", "success")
        else:
            fl.flash("Failed to update", "error")
            fl.flash(str(form.errors), 'error')
            fl.flash(str(new_chinese_file.errors), 'error')
        return fl.render_template('analyst/stage4.html', form=form,t=t_db,\
        new_chinese_file= new_chinese_file,new_counter_file = new_counter_file, \
        new_counter_file_tb= new_counter_file_tb, new_chinese_file_tb= new_chinese_file_tb)



def roster():
    import forms as fm
    #to store no of hours available per week for analyst
    form = fm.roster(fl.request.form)
    from datetime import datetime, timedelta
    today = datetime.now().date()
    start_this_week = today - timedelta(days=today.weekday())
    start = start_this_week + timedelta(days=7)
    if fl.request.method == 'GET':
        update_calendar()

        form.end_date.choices = [(cal.end_date,cal.end_date.strftime('%Y-%m-%d')) for cal in ml.Calendar.query.filter_by(start_date=start).all()]
        return fl.render_template('analyst/roster.html', form=form)
    else:
        r = ml.Roster()

        user_id = fl.session['logged_in']
        start_date = fl.request.form['start_date']
        start_time = '00:00:00'
        start = start_date +' '+ start_time
        start1 = datetime.strptime(start, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        form.end_date.choices = [(cal.end_date,cal.end_date.strftime('%Y-%m-%d')) for cal in ml.Calendar.query.filter_by(start_date=start).all()]

        #end_date = fl.request.form['end_date']
        no_of_hours = fl.request.form['no_of_hours']
        #wid = ml.Calendar.query.get(start_date)
        wid = ml.Calendar.query.filter_by(start_date=start1).first()
        r.user_id = user_id
        r.week_id = wid.id
        r.no_of_hours = no_of_hours
        cid = ml.Roster.query.filter_by(user_id=user_id,week_id = wid.id ).first()
        #if condition to insert new entry
        if(cid is None):
            db.db_session.add(r)
        else:
        # if its an existing r=entry update record by deleting and re entring the record
            updated_week_id = wid.id
            rost = ml.Roster.query.filter_by(user_id=user_id,week_id = wid.id ).first()
            db.db_session.delete(rost)
            db.db_session.add(r)
        db.db_session.commit()
        fl.flash("Updated roster", "success")
        return fl.render_template('analyst/roster.html', form=form)




# implementation of the search-for-id and return id, name function
def search_id(id):
    id = str(id)
    res = ml.User.query.get(id)
    return js.dumps([res.id, res.fname, res.lname])


# implementation of the searching for a username with some query function
def search_username(query):
    res = ml.User.query.filter(ml.User.fname.like("%{0}%".format(query))).all()
    ret = []
    for r in res:
        ret.append([r.id, r.fname, r.lname])
    return fl.jsonify(ret)

# implememt for getting week end date when passed week current date
def search_enddate(start_date):
    #cities = City.query.filter_by(state=state).all()

    end_date = ml.Calendar.query.filter_by(start_date=start_date).all()

    endArray = []

    for end in end_date:
        endObj = {}
        endObj['id'] = end.end_date.strftime('%Y-%m-%d %H:%M:%S')
        endObj['end_date'] = end.end_date.strftime('%Y-%m-%d')
        endArray.append(endObj)

    return fl.jsonify({'End_Date' : endArray})

# to insert into calendar for next 6 mmonths
# need to figure out where its should be called
# presently called in roster (get method)
def update_calendar():

    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta

    today = datetime.now().date()
    six_months = today + relativedelta(months=+6)
    while (today <= six_months):
        start_this_week = today - timedelta(days=today.weekday())
        start = start_this_week + timedelta(days=7)
        weekNumber = today.isocalendar()[1]
        y = today.year
        today = today + timedelta(days=7)
        id = int(str(y) + str(weekNumber));
        start_date = start
        end_date = start + timedelta(days=6)
        wid = ml.Calendar.query.filter_by(id=id).first()

        if(wid is None):
            cal = ml.Calendar(start_date=start_date, end_date=end_date, id=id)
            db.db_session.add(cal)
    db.db_session.commit()


def master_sheet():
    import forms as fm
    form = fm.master_sheet(fl.request.form)
    if fl.request.method == 'GET':
        return fl.render_template('master_sheet.html',form= form)
    else:
        IID = int(fl.request.form['IID'])
        s1 = ml.Transactions.query.filter_by(s_id = IID).all()
        s_rels = ml.Stage_Rels.query.get(IID)
        s2 = ml.Stage_2.query.filter_by(s_id = s_rels.stage_2_id).all()
        s3 = ml.Stage_3.query.filter_by(s_id = s_rels.stage_3_id).all()
        s4 = ml.Stage_4.query.filter_by(s_id = s_rels.stage_4_id).all()
        cf = ml.Chinese_Investor_File.query.filter_by(linked_iid = IID).all()
        cof = ml.Counterpart_Investor_File.query.filter_by(linked_iid = IID).all()
        return fl.render_template('master_sheet.html', form= form, s1 = s1, s2= s2, s3=s3, s4= s4,cf =cf,cof = cof)

def stage_check():
    import forms as fm
    if fl.session['admin']:
        if fl.request.method == 'GET':
            s2 = ml.Stage_2.query.filter(ml.Stage_2.state == "Pending").all()
            s4 = ml.Stage_4.query.filter(ml.Stage_4.state == "Pending").all()
            return fl.render_template('leadanalyst/stage_check.html', stage2=s2, stage4 = s4)
        else:
            return fl.abort(404)
    else:
        return fl.abort(404)



def stage_2_details(s_id):
    import forms as fm

    #s_rels = ml.Stage_Rels.query.get(IID)
    #s_rels = ml.Stage_Rels.query.filter_by(stage_2_id = s_id).all()
    s_rels = ml.Stage_Rels.query.filter_by(stage_2_id = s_id ).first()
    s1 = ml.Transactions.query.filter_by(s_id = s_rels.trans_id).first()
    s2 = ml.Stage_2.query.filter_by(s_id = s_rels.stage_2_id).first()
    #cf = ml.Chinese_Investor_File.query.filter_by(linked_iid = IID).all()
    #cof = ml.Counterpart_Investor_File.query.filter_by(linked_iid = IID).all()
    if fl.session['admin']:
        if fl.request.method == 'GET':
            return fl.render_template('leadanalyst/stage_2_details.html',trans = s1, s2= s2)
        else:
            try:
                state = fl.request.form['state']
            except KeyError:
                state = None
            if state == '1':
                s2.state = State.Accepted
            elif state == '2':
                s2.state = State.Rejected
            else:
                state = ''
            db.db_session.add(s2)
            db.db_session.commit()
            t_db = ml.Stage_2.query.get(s2.s_id)
            # we want to add the transition to s3
            if t_db.state == State.Accepted:

                s3 = transition_transaction(t_db)
            s2_check = ml.Stage_2.query.filter(ml.Stage_2.state == "Pending").all()
            s4_check = ml.Stage_4.query.filter(ml.Stage_4.state == "Pending").all()
            return fl.render_template('leadanalyst/stage_check.html', stage2=s2_check, stage4 = s4_check)
    else:
        return fl.abort(404)

def stage_4_details(s_id):
    import forms as fm

    #s_rels = ml.Stage_Rels.query.get(IID)
    #s_rels = ml.Stage_Rels.query.filter_by(stage_2_id = s_id).all()
    form = fm.stage_4_details(fl.request.form)
    s_rels = ml.Stage_Rels.query.filter_by(stage_4_id = s_id ).first()
    s1 = ml.Transactions.query.filter_by(s_id = s_rels.trans_id).first()
    s2 = ml.Stage_2.query.filter_by(s_id = s_rels.stage_2_id).first()
    s3 = ml.Stage_3.query.filter_by(s_id = s_rels.stage_3_id).first()
    s4 = ml.Stage_4.query.filter_by(s_id = s_rels.stage_4_id).first()

    if fl.session['admin']:
        if fl.request.method == 'GET':
            return fl.render_template('leadanalyst/stage_4_details.html',trans = s1, s2= s2, s3= s3, s4= s4)
        else:
            try:
                state = fl.request.form['state']
            except KeyError:
                state = None
            if state == '1':
                s4.state = State.Accepted
            elif state == '2':
                s4.state = State.Rejected
            else:
                state = ''
            db.db_session.add(s4)
            db.db_session.commit()
            t_db = ml.Stage_4.query.get(s4.s_id)
            # we want to add the transition to s3
            if t_db.state == State.Accepted:

                s = transition_transaction(t_db)
            s2_check = ml.Stage_2.query.filter(ml.Stage_2.state == "Pending").all()
            s4_check = ml.Stage_4.query.filter(ml.Stage_4.state == "Pending").all()
            return fl.render_template('leadanalyst/stage_check.html', stage2=s2_check, stage4 = s4_check)
    else:
        return fl.abort(404)



# ================
# allocation logic

def allocate_transactions(dataset):
    """take any dataset and allocate any unallocated transactions to
    all the people"""
    if not(fl.session['admin']):
        fl.flash("You must be an admin to do this!")
        return fl.redirect(fl.url_for('index'))

    # get all the transactions which relate to the dataset
    all_trans = []
    transactions = ml.Transactions.query.filter(ml.Transactions.dataset_id == \
    dataset).order_by(sa.desc(ml.Transactions.stage)).all()
    for t in transactions:
        all_trans.append(t)

    for t in transactions:
        c_sr = ml.Stage_Rels.query.filter(ml.Stage_Rels.trans_id == t.s_id).first()
        if not c_sr.stage_2_id == None:
            all_trans.append(ml.Stage_2.query.get(c_sr.stage_2_id))
        elif not c_sr.stage_3_id == None:
            all_trans.append(ml.Stage_3.query.get(c_sr.stage_3_id))
        else:
            pass
    print(str(all_trans))

    # CONSIDER tasks LAST!
    # get admin user id
    la = ml.User.query.filter(ml.User.admin).first() # should only be 1!

    tasks = ml.Tasks.query.filter(ml.Tasks.who_assigned == la.id).all()
    # ones allocated to the LA are able to be manually allocated (because owned
    # by the LA) but we want them to be allocated to someone else automatically
    # get the roster for the next week
    for t in tasks:
        all_trans.append(t)
    cur_week = get_week_id(dt.datetime.now())
    roster = ml.Roster.query.filter(ml.Roster.week_id == cur_week+1).all()
    users = []
    u_count = 0 # user count
    for r in roster:
        users.append([r.user_id, r.no_of_hours])
    # check the settings to figure out which method we'll use to process the
    # queue.
    if ml.Admin.query.filter(ml.Admin.prefer_all_stages).first() == None:
        # preference is to get stages to stage 5 as soon as possible.
        # allocate transactions first, then tasks
        # simply, while transactions and users remain, allocate a user to
        # a transaction

        for u in users:
            user = ml.User.query.filter(ml.User.id == u[0]).first()
            fl.flash("user: "+str(user.fname))
            for t in all_trans:
                if t.stage != 1:
                    m_r = t.mandarin_req
                else:
                    m_r = False
                if not m_r:
                    while u[1] >= user.avg_time_to_complete:
                        u[1] -= user.avg_time_to_complete
                        t.who_assigned = u[0]
                        db.db_session.add(t)
                        # adjust roster
                        for r in roster:
                            if r.user_id == u[0] and r.no_of_hours == u[1]:
                                r.already_allocated += user.avg_time_to_complete
                                db.db_session.add(r)
                    # now move on to the next task - user expired!
                else:
                    pass # deal with mandarin later!

        # for t in all_trans:
        #     ct_trans = 0 # count tasks
        #     # trans in descending order; allocate
        #     if not t.mandarin_req:
        #
        #         if u_count < len(users):
        #             cur = users[u_count]
        #         else:
        #             break
        #
        #         u = ml.User.query.get(cur[0])
        #         print("allocating user")
        #         tasks_remain = True
        #         while (cur[1] >= u.avg_time_to_complete) & tasks_remain:
        #             cur[1] -= u.avg_time_to_complete
        #             # get appropriate user
        #             t.who_assigned = u.id
        #             db.db_session.add(t)
        #             ct_trans += 1
        #
        #             # now set the allocated var to true in the roster
        #             roster[u_count].already_allocated +=u.avg_time_to_complete
        #             db.db_session.add(roster[u_count])
        #
        #             print("allocated "+u.fname+" to "+str(t.s_id))
        #
        #             if ct_trans == len(transactions):
        #                 # just make sure we have more trans before allocating
        #                 print("prepare to break")
        #                 tasks_remain = False
        #
        #         u_count+=1
        #
        #
        #     else:
        #         pass # not allocating mandarin ones yet. To come
        db.db_session.commit()
        fl.flash("Allocated", "success")
        return fl.redirect(fl.url_for('index'))
    else:
        pass


# dataset & tasks created, so we need to allocate analysts to the tasks
# inputs: dataset id, analyst availability, time delta of the
        # dataset, frequency
# output: modified database where each task is allocated to exactly 1 task
def allocate_tasks_analysts(d_id):
    if 'admin' not in fl.session:
        fl.flash('This operation is restricted to lead analysts', 'error')
        return fl.redirect(fl.url_for('index'))

    # get all the tasks related to this dataset
    tasks = ml.Tasks.query.filter(ml.Tasks.dataset_owner == d_id).all()
    # now get the dataset
    ds = ml.Dataset.query.get(d_id)

    # get current week id
    cur_date = dt.datetime.now() # today's date

    # get the analyst availability for the next two weeks
    # 1. get the current week
    # 2. get the next two week roster array
    wk_id = get_week_id(cur_date) # gets the current week id

    aa = ml.Roster.query.filter(sa.or_(ml.Roster.week_id == (wk_id+1), \
    ml.Roster.week_id == (wk_id+2))).all()
    # presumes that there should be one week which uniquely matches constraints

    # go through each user and allocate as many hours as they can take
    # while there are still tasks remaining that they can do
    # get users who are avilable during this time
    users = []
    for entry in aa:
        if not entry.already_allocated:
            users.append([entry.user_id, entry.no_of_hours, entry.week_id])

    # now allocate as much work as we can for every user
    current_task_ct = 0
    tasks_remain = True
    for user in users:
        if tasks_remain:
            # get user
            u = ml.User.query.get(user[0])
            # get user avg_time_to_complete. presumes only one will be returned
            attc = u.avg_time_to_complete
            # get num hours available
            num_hours = user[1] # no need to add in the hours
            print("num hours to complete: "+str(num_hours))
            while (num_hours >= attc) & tasks_remain:
                # allocate the user their weekly amount of tasks
                # their number of hours available - task attc for every one
                tasks[current_task_ct].who_assigned = u.id
                # get the current task's transactions number
                num_trans = len(tasks[current_task_ct].trans)
                # if at stage 1, then expect no transactions yet
                # SO allocate using traditioanl metric.
                # BUT, if not, then we should have transactions and so we
                # will subtract the number of transactions * the attc

                db.db_session.add(tasks[current_task_ct])
                current_task_ct += 1
                num_hours -= attc
                if (current_task_ct >= len(tasks)):
                    tasks_remain = False
            # allocation of user is done for this period
            # to do so, fetch the right roster entry again...
            u_adj = ml.Roster.query.filter(sa.and_(sa.and_(ml.Roster.user_id == u.id, \
            ml.Roster.no_of_hours == user[1]), ml.Roster.week_id == user[2])).first()
            u_adj.already_allocated = True

            db.db_session.add(u_adj)

            # send user an email
            em = s.send_user(user[0], "CHIIA: New Task!", \
            "Hi there "+u.fname+", \n You've been allocated a new task. \
            Please check the website for details. Thanks!", False)
    try:
        db.db_session.commit()
        fl.flash('Manually allocated for next two weeks', 'success')
    except Exception as e:
        fl.flash('Manual allocation failed with error: '+str(e), 'error')
        db.db_session.flush()

    return fl.redirect(fl.url_for('manage_datasets'))


# allocate on a user level i.e get trans_id then get the right stage then
# allocate a stage/trans to the next person
def allocate_user(trans, mandarin):
    t = ml.Transactions.query.get(trans.s_id)

    # temp measure
    t = ml.Tasks.query.get(t.tasks).who_assigned
    if t == None:
        return None
    else:
        return t

def transition_transaction(trans):
    """take the current transaction and move the user between this stage and
    the next"""
    if trans.stage == 1:
        # moving into stage 2

        # get new ID
        s2_id = db.db_session.query(sa.func.max(ml.Stage_2.s_id)).scalar()
        if s2_id:
            s2_id+=1
        else:
            s2_id=1

        s2 = ml.Stage_2(s_id=s2_id, state=State.Working)

        # no email or approval required, so just allocate the next user
        new = allocate_user(s2, trans.mandarin_req)
        if new:
            s2.who_assigned = new
            # email user that they have the task now

            s.send_user(new, "New Transaction!",  "Hello, here is a new \
            transaction for you __>here<__.", False)
        else:
            fl.flash("Unable to allocate user to transaction", "error")


        # NOTE: check here for whether the analyst says we need a
        # mandarin reader to do this or else we reallocate.
        db.db_session.add(s2)

        # now join it to the sr table with the new trans
        sr = ml.Stage_Rels(trans_id=trans.id, stage_2_id=s2.s_id)
        db.db_session.add(sr)

        try:
            db.db_session.commit()
            fl.flash(fl.Markup("Transaction accepted! New stage <a href="+fl.url_for('stage2', s_id=s2_id)+">here</a>"), "success")
        except sa.exc.InvalidRequestError:
            fl.flash("Failed to transition into stage two", "error")

        return s2
    elif trans.stage == 2:
        # progression to s3 is less simple. if the LA has already accepted
        # the task, then move on but otherwise interact with
        # state to determine what to do.

        # CHECK! has it already been accepted by the LA?
        if trans.state == State.Accepted:

            s3_id = db.db_session.query(sa.func.max(ml.Stage_3.s_id)).scalar()
            if s3_id:
                s3_id += 1
            else:
                s3_id = 1

            s3 = ml.Stage_3(s_id=s3_id)

            user = allocate_user(trans, False)
            if user:
                s3.who_assigned = user
            else:
                fl.flash("Unable to allocate user!", "error")

            # get the ID of the transaction which is the parent to this overall
            # transaction
            sr = trans.stage_2_id[0] #get's the SR object!
            # master = ml.Stage_Rels.query.filter(ml.Stage_Rels.stage_2_id \
            # == t_id).first().trans_id

            # sr = ml.Stage_Rels.query.filter(ml.Stage_Rels.trans_id == master & \
            # ml.Stage_Rels.stage_2_id == trans.s_id).all() #should only be one!

            # now we want to update it
            # if len(sr) == 1:
            sr.stage_3_id = s3_id
            db.db_session.add(s3)
            db.db_session.add(sr)

            fl.flash(fl.Markup("Transaction accepted! New stage <a href="+\
            fl.url_for('stage3', s_id=s3_id)+">here</a>"), "success")

            db.db_session.commit()

        elif trans.state == State.Pending:
            fl.flash("Lead Analyst is yet to accept", "error")
            return -1
        elif trans.state == State.Rejected:
            fl.flash("Work rejected.", "success")
            if s.send_user(trans.who_assigned, "Work Failed!", "Hi there, \
            Your work for transaction "+str(trans.s_id)+" @ stage 2 has been \
            rejected. Please log in to resolve and resubmit. Thank you.") != 202:
                fl.flash("Server error! Email failed to send.", "error")

            # assume staying with same person
            trans.state = State.Working

            db.db_session.add(trans)
            db.db_session.commit()
            return trans

        elif trans.state == State.Working:
            # state == working so we need to actually kick off the process of
            # getting the LA to accept :)

            # get LA ID
            la = ml.User.query.filter(ml.User.admin).first()
            s.send_user(la.id, "Checkpoint for transactions!", "Hey there, \
            there's a new submission that needs to be checked for the \
            transaction. See the website for more details.", False)

            fl.flash("Lead analyst contacted.", "success")

            # state change
            trans.state = State.Pending
            db.db_session.add(trans)

            db.db_session.commit()
            return trans
        else:
            fl.flash("Server error DEBUG="+str(trans.s_id)+", stage="+str(trans.state), "error")
            return -1

    elif trans.stage == 3:
        s4_id = db.db_session.query(sa.func.max(ml.Stage_4.s_id)).scalar()
        if s4_id:
            s4_id += 1
        else:
            s4_id = 1

        s4 = ml.Stage_4(s_id = s4_id, state=State.Working)

        # we need to allocate this to a user, so allocate.
        u = allocate_user(trans, trans.mandarin_req)
        s4.who_assigned = u

        db.db_session.add(s4)

        # update the stage relations
        sr = ml.Stage_Rels.query.filter(ml.Stage_Rels.stage_3_id == \
        trans.s_id).first()
        sr.stage_4_id = s4_id
        db.db_session.add(sr)

        fl.flash(fl.Markup("Transaction accepted! New stage <a href="+fl.url_for('stage4', s_id=s4_id)+">here</a>"), "success")
        db.db_session.commit()
        return s4

    elif trans.stage == 4:
        # ==========
        # RULES
        # ==========

        # MUST PASS LA check, so check whether the LA has

        # CHECK! has it already been accepted by the LA?
        if trans.state == State.Accepted:
            fl.flash("Transaction accepted!", "success")
            # get the new id for stage 4
            return trans

        elif trans.state == State.Pending:
            fl.flash("Lead Analyst is yet to accept", "error")
            return trans
        elif trans.state == State.Rejected:
            fl.flash("Work rejected.", "success")
            if s.send_user(trans.who_assigned, "Work Failed!", "Hi there, \
            your work for transaction "+str(trans.s_id)+" @ stage 2 has been \
            rejected. Please log in to resolve and resubmit. Thank you.") != 202:
                fl.flash("Server error! Email failed to send.", "error")

            # assume staying with same person
            trans.state = State.Working

            db.db_session.add(trans)
            db.db_session.commit()
            return trans

        elif trans.state == State.Working:
            # state == working so we need to actually kick off the process of
            # getting the LA to accept :)

            # get LA ID
            la = ml.User.query.filter(ml.User.admin).first()
            s.send_user(la.id, "Checkpoint for transactions!", "Hey there, \
            there's a new submission that needs to be checked for the \
            transaction. See the website for more details. Ben.", False)

            fl.flash("Lead analyst contacted.", "success")

            # state change
            trans.state = State.Pending
            db.db_session.add(trans)

            db.db_session.commit()
            return trans
        else:
            fl.flash("Server error DEBUG="+str(trans.s_id)+", stage="+str(trans.state), "error")
            return -1

def get_week_id(cur_date):
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta

    cur = cur_date.date()
    weekNumber = cur.isocalendar()[1]
    y = cur.year
    return int(str(y) + str(weekNumber))
