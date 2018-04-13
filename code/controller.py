import flask as fl
import database as db

def login():
    import models as mod
    new_user = mod.User()
    db.db_session.add(new_user)
    db.db_session.commit()
    return fl.render_template('/login.html')
