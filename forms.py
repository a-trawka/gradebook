from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired


class TeacherEditForm(FlaskForm):
    first_name = StringField('first_name', validators=[InputRequired()])
    last_name = StringField('last_name', validators=[InputRequired()])