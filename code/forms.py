# this page will contain forms using the form-wtf plugin for Flask
# Classes represent individual quizes and then fields are the vars
# inside each class.

import flask_wtf as wtf
import models as ml
from wtforms import StringField, IntegerField, SelectField, DateField, FloatField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Required, NumberRange

class Settings_Search(wtf.FlaskForm):
    search_name = StringField('name', validators=[DataRequired()])

class Create_Dataset(wtf.FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    # get the search types available
    res = ml.Search_Names.query.all()
    search_type = SelectField(u'Search Type', coerce=str, validators=[Required("Please enter your name.")], choices=[(str(r.id), r.name) for r in res])
    year_start = DateField('year_start', validators=[Required("Please enter the correct date.")], format='%Y')
    year_end = DateField('year_end', validators=[Required("Please enter the correct date.")], format='%Y')
    access = IntegerField('access_id')
    freq_opt = ml.Frequencies.query.all()
    freq = SelectField(u'freq', coerce=int, validators=[DataRequired("Please decide the frequency")], choices=[(f.id, f.name) for f in freq_opt])

class Edit_Dataset(wtf.FlaskForm):
    name = StringField('name')
    # get the search types available
    res = ml.Search_Names.query.all()
    search_type = SelectField(u'Search Type', coerce=str, choices=[(str(r.id), r.name) for r in res])
    year_start = DateField('year_start')
    year_end = DateField('year_end')
    access = IntegerField('access_id')

class Create_Transaction(wtf.FlaskForm):
    name = StringField('name', [DataRequired()])
    amount = FloatField('amount', [DataRequired()])

    #prefill this with the filled value of the current user
    who_assigned = IntegerField('who_assigned', [DataRequired()])
    who_previous_stages = StringField('who_previous_stages')

    # hiddens
    dataset_id = HiddenField('ds_id')
    task_id = HiddenField('t_id')

class Edit_Task(wtf.FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired("Please ensure you've entered a name")])
    date_start = DateField('date_start', format='%Y', validators=[DataRequired("This date cannot be empty")])
    date_end = DateField('date_end', format='%Y', validators=[DataRequired("This date cannot be empty")])
    who_assigned = IntegerField('who_assigned')
    dataset_owner = StringField('dataset_owner', validators=[DataRequired("The dataset must have an owner")])


# chin_inv_file_no = FloatField('chin_inv_file_no', \
# validators=[NumberRange(0, 99999999, "Invalid file number")])
# counterpart_file_no = FloatField('counterpart_file_no', \
# validators=[NumberRange(0, 99999999, "Invalid file number")])
