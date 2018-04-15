import flask as fl
import database as db

def login():
    import models as mod
    new_user = mod.User()
    db.db_session.add(new_user)
    db.db_session.commit()
    user = mod.User.query.order_by(mod.User.id.desc()).first()
    return fl.render_template('/login.html', user=user)
