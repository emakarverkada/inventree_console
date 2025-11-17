from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired


class InvTrackingForm(FlaskForm):
    name = SelectField("Name")
    location = SelectField("Location")
    serials = StringField("Serials")
    check_in = SubmitField("Check In")
    check_out = SubmitField("Check Out")
