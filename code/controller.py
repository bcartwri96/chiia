import flask as fl
import database as db
import models as mod

def login():
    import datetime
    current = datetime.datetime.now()
    new_user = mod.User()
    db.db_session.add(new_user)
    db.db_session.commit()
    user = mod.User.query.order_by(mod.User.id.desc()).first()
    return fl.render_template('/login.html', user=user, current=current)
