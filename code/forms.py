# this page will contain forms using the form-wtf plugin for Flask
import flask_wtf as wtf
import models as ml
from wtforms import StringField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, EqualTo, Required

class Settings_Search(wtf.FlaskForm):
    search_name = StringField('name', validators=[DataRequired()])


class Create_Dataset(wtf.FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    # get the search types available
    res = ml.Search_Names.query.all()
    search_type = SelectField(u'Search Type', coerce=str, validators=[Required("Please enter your name.")], choices=[(str(r.id), r.name) for r in res])
    year_start = DateField('year_start', validators=[Required("Please enter the correct date.")], format='%Y')
    year_end = DateField('year_end', validators=[Required("Please enter the correct date.")], format='%Y')
    access = IntegerField('access_id', validators=[DataRequired()])


    # id = sa.Column(sa.Integer, primary_key=True)
    # name = sa.Column(sa.String, nullable=False)
    # search_type = sa.Column(sa.String, nullable=False)
    # user_created = sa.Column(sa.Integer, nullable=False)
    # time_created = sa.Column(sa.DateTime, nullable=False)
    # year_start = sa.Column(sa.DateTime, nullable=False)
    # year_end = sa.Column(sa.DateTime, nullable=False)
    # access = sao.relationship("Dataset_Authd", backref='dataset', lazy=True)
