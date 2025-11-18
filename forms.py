from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, FieldList, validators
import regex as re

# Pattern: 1-4 alphanumeric chars, dash, 1-4 alphanumeric chars, dash, 1-4 alphanumeric chars
SERIAL_PATTERN = r"^[A-Za-z0-9]{1,4}-[A-Za-z0-9]{1,4}-[A-Za-z0-9]{1,4}$"


def validate_serial(form, field):
    """
    Validate that a serial matches the format ****-****-**** with 4 or fewer chars per segment.
    """
    if not field.data or not field.data.strip():
        return  # Empty is allowed (will be filtered out)

    serial = field.data.strip()
    if not re.match(SERIAL_PATTERN, serial):
        raise validators.ValidationError(f'Serial "{serial}" does not match the required format "****-****-****" (each segment must be 1-4 alphanumeric characters)')


class InvTrackingForm(FlaskForm):
    name = SelectField("Name")
    location = SelectField("Location")
    serials = FieldList(StringField("Serial Number", validators=[validate_serial]), min_entries=1, label="Serial Numbers")
    check_in = SubmitField("Check In")
    check_out = SubmitField("Check Out")
