import re
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, FieldList, validators

# Pattern: 1-4 alphanumeric chars, dash, 1-4 alphanumeric chars, dash, 1-4 alphanumeric chars
SERIAL_PATTERN = r"^[A-Za-z0-9]{1,4}-[A-Za-z0-9]{1,4}-[A-Za-z0-9]{1,4}$"


def validate_serial(form, field):
    """
    Validate that a serial matches the format ****-****-**** with 4 or fewer chars per segment.
    Empty fields are allowed (will be filtered out by form-level validation).
    """
    # Allow empty fields - they will be filtered out by _clean_serials()
    if not field.data or not field.data.strip():
        return

    serial = field.data.strip()
    if not re.match(SERIAL_PATTERN, serial):
        raise validators.ValidationError(f'Serial "{serial}" does not match the required format "****-****-****" ' f"(each segment must be 1-4 alphanumeric characters)")


class InvTrackingForm(FlaskForm):
    name = SelectField("Name", validators=[validators.DataRequired(message="Please select a name")])
    location = SelectField("Location", validators=[validators.DataRequired(message="Please select a location")])
    serials = FieldList(StringField("Serial Number", validators=[validate_serial]), min_entries=1, label="Serial Numbers")
    check_in = SubmitField("Check In")
    check_out = SubmitField("Check Out")

    def _clean_serials(self):
        """
        Internal method to collect and clean serial numbers.

        Returns:
            List of cleaned serial numbers (stripped, non-empty, deduplicated)
        """
        serials = []
        for serial_field in self.serials:
            serial_value = serial_field.data.strip() if serial_field.data else ""
            if serial_value:
                serials.append(serial_value)

        # Remove duplicates while preserving order
        seen = set()
        return [s for s in serials if s not in seen and not seen.add(s)]

    def validate_serials(self, field):
        """
        Form-level validator to ensure at least one valid serial number is provided.
        """
        cleaned_serials = self._clean_serials()
        if not cleaned_serials:
            raise validators.ValidationError("Please provide at least one valid serial number")

    def get_cleaned_serials(self):
        """
        Get cleaned list of serial numbers (stripped, non-empty, deduplicated).

        Returns:
            List of cleaned serial numbers
        """
        return self._clean_serials()
