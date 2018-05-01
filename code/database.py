# this file defines the way the database will be setup
from flask import Flask as fl
from flask_sqlalchemy import SQLAlchemy
import os
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
app = fl(__name__)

#############################################################
# model support code
#############################################################

def resetdb():
    """Destroys and creates the database + tables."""

    metadata = sa.MetaData()
    metadata.reflect(engine)
    for tbl in reversed(metadata.sorted_tables):
        tbl.drop(engine)
    # if not database_exists(DB_URL):
    #     print('Creating database.')
    #     create_database(DB_URL)

    print('Creating tables.')
    # import the models used to describe the tables we're creating (using the
    # ORM). Link: http://flask-sqlalchemy.pocoo.org/2.3/models/
    import models
    Base.metadata.create_all(bind=engine)
    db_session.commit()
    print('Integrating models.')

    # create user object and then commit to db
    from passlib.hash import sha512_crypt
    pw_hashed = sha512_crypt.encrypt("admin")
    pw_hashed_an = sha512_crypt.encrypt("test")
    new_admin = models.User(fname="Johnny", lname="Admin", email="bcartwri96@gmail.com", language=False, pw_hashed=pw_hashed, admin=True, confirmed=True)
    new_analyst = models.User(fname="Johny", lname="Test", email="test@test.com", language=True, pw_hashed=pw_hashed_an, admin=False)
    db_session.add(new_admin)
    db_session.add(new_analyst)
    update = models.Admin()
    new_search_names = models.Search_Names(name="Factiva")
    update.search_names.append(new_search_names)
    db_session.add(update)
    db_session.commit()
    print("Creating an admin user.")
    print("Creating an test user.")
    print("Creating a new search type")

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)


#############################################################
# setup - run python; import database; database.resetdb() to reset db
#############################################################

# the values of those depend on your setup
POSTGRES_URL = get_env_variable("POSTGRES_URL")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PW = get_env_variable("POSTGRES_PW")
POSTGRES_DB = get_env_variable("POSTGRES_DB")
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

# when sending to the REAL WORLD!
try:
    DATABASE_URL = get_env_variable("DATABASE_URL")
    DB_URL = DATABASE_URL
except Exception:
    pass

engine = create_engine(DB_URL, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
