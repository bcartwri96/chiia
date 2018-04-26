# this page will contain forms using the form-wtf plugin for Flask
import flask_wtf as wtf
from wtforms import StringField
from wtforms.validators import DataRequired, EqualTo

class Settings_Search(wtf.Form):
    search_name = StringField('name', [DataRequired()])
