# this page will contain forms using the form-wtf plugin for Flask
# Classes represent individual quizes and then fields are the vars
# inside each class.

import flask_wtf as wtf
import models as ml
from wtforms import StringField, IntegerField, SelectField, DateField, \
FloatField, HiddenField, BooleanField, SubmitField
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
    amount = FloatField('amount')

    # creating Transactions
    anouncement_date = DateField('annoucement', format='%d-%m-%Y', validators=[DataRequired(message='You need to enter a date of format d-m-y')],)
    entity_name = StringField('entity_name', validators=[DataRequired(message="You need to enter an entity name")])
    rumour_date = DateField('rumour', format='%d-%m-%Y', validators=[DataRequired(message='You need to enter a date of format d-m-y')],)
    mandarin = BooleanField('mandarin')

    #prefill this with the filled value of the current user
    who_assigned = IntegerField('who_assigned', [DataRequired()])
    who_previous_stages = StringField('who_previous_stages')

    # hiddens
    dataset_id = HiddenField('ds_id')
    task_id = HiddenField('t_id')

    # check which form was submitted
    trans_submitted = SubmitField('Submit Transaction')

class Edit_Task(wtf.FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired("Please ensure you've entered a name")])
    date_start = DateField('date_start', format='%Y', validators=[DataRequired("This date cannot be empty")])
    date_end = DateField('date_end', format='%Y', validators=[DataRequired("This date cannot be empty")])
    who_assigned = IntegerField('who_assigned')
    search_term = StringField('search_term', validators=[DataRequired()])
    dataset_owner = StringField('dataset_owner', validators=[DataRequired("The dataset must have an owner")])

    task_submitted = SubmitField('Submit the Task')

class stage1(wtf.FlaskForm):
    date_conducted = DateField('date_conducted', format='%Y', validators=[DataRequired("This date cannot be empty")])
    nickname = StringField('nickname', validators=[DataRequired("Please ensure you've entered a name")])
    search_term = StringField('search_term', validators=[DataRequired()])
    date_start = DateField('date_start', format='%Y', validators=[DataRequired("This date cannot be empty")])
    date_end = DateField('date_end', format='%Y', validators=[DataRequired("This date cannot be empty")])
    no_of_result_to_s2 = IntegerField('no_of_result_to_s2', validators=[DataRequired("This column cannot be empty")])
    total_no_of_result = IntegerField('total_no_of_result', validators=[DataRequired("This  column cannot be empty")])
#    dataset_owner = StringField('dataset_owner', validators=[DataRequired("The dataset must have an owner")])
    task_submitted = SubmitField('Submit')


class stage2(wtf.FlaskForm):

    S2_date = DateField('S2_date', format='%Y', validators=[DataRequired("This date cannot be empty")])
    S2_reviews = IntegerField('S2_reviews', validators=[DataRequired("This column cannot be empty")])
    chin_inv_file_no = IntegerField('chin_inv_file_no', validators=[DataRequired("This column cannot be empty")])
    counterpart_file_no = IntegerField('counterpart_file_no', validators=[DataRequired("This column cannot be empty")])



#    dataset_owner = StringField('dataset_owner', validators=[DataRequired("The dataset must have an owner")])
    task_submitted = SubmitField('Submit the Task')

class stage3(wtf.FlaskForm):

    S3_date = DateField('S3_date', format='%Y', validators=[DataRequired("This date cannot be empty")])
    S3_reviews = IntegerField('S3_reviews', validators=[DataRequired("This column cannot be empty")])
    dataset_type = StringField('dataset_type', validators=[DataRequired("Please select dataset type")])
#    dataset_owner = StringField('dataset_owner', validators=[DataRequired("The dataset must have an owner")])
    task_submitted = SubmitField('Submit the Task')


class stage4(wtf.FlaskForm):

    S4_date = DateField('S4_date', format='%Y', validators=[DataRequired("This date cannot be empty")])
    S4_reviews = IntegerField('S4_reviews', validators=[DataRequired("This column cannot be empty")])

    chin_inv_file_no = IntegerField('chin_inv_file_no', validators=[DataRequired("This column cannot be empty")])
    counterpart_file_no = IntegerField('counterpart_file_no', validators=[DataRequired("This column cannot be empty")])
#    dataset_owner = StringField('dataset_owner', validators=[DataRequired("The dataset must have an owner")])
    task_submitted = SubmitField('Submit the Task')



    # chin_inv_file_no = FloatField('chin_inv_file_no', \
    # validators=[NumberRange(0, 99999999, "Invalid file number")])
    # counterpart_file_no = FloatField('counterpart_file_no', \
    # validators=[NumberRange(0, 99999999, "Invalid file number")])
