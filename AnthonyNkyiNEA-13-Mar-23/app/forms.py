from app.models import Doctor, Patient
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, IntegerRangeField, DateField, TimeField, TextAreaField, IntegerField, SelectMultipleField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError, DataRequired, NumberRange
from datetime import date, time, datetime, timedelta

#login form for webpage
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(),Length(min=3,max=32),Email()])
    password = PasswordField('Password', validators=[InputRequired(),Length(min=8,max=80)])
    remember = BooleanField('Remember me?')
    submit = SubmitField('Sign in')

#book appointment: default is next day
class AppointmentForm(FlaskForm):
    appdate = DateField('Date:',default=(date.today()+timedelta(days=1)),format='%Y-%m-%d',validators=[InputRequired()])
    apptime = TimeField('Time:',format='%H:%M',validators=[InputRequired()])
    submit = SubmitField('Request')
    
    def validate_appdate(form,field):
        if (field.data) <= date.today():
            print('ok')
            raise ValidationError('Appointment cannot be booked in the past.')

class DoctorAppointmentForm(FlaskForm):
    patient = SelectField('Patient', choices=[])
    appdate = DateField('Date:',default=(date.today()+timedelta(days=1)),format='%Y-%m-%d',validators=[InputRequired()])
    apptime = TimeField('Time:',format='%H:%M',validators=[InputRequired()])
    approom = StringField('Room:',validators=[InputRequired(),Length(min=1,max=4)])
    submit = SubmitField('Book')
    
    def validate_appdate(form,field):
        if (field.data) <= date.today():
            print('ok')
            raise ValidationError('Appointment cannot be booked in the past.')

class PatientAllergyForm(FlaskForm):
    allergy = StringField('Allergy', validators=[InputRequired()])
    severity = IntegerField('Severity',validators=[InputRequired(),NumberRange(min=1,max=5)])
    submit = SubmitField('Submit')

class MedicineAllergyForm(FlaskForm):
    medicine = StringField('Medicine', validators=[InputRequired()])
    allergen = StringField('Allergen', validators=[InputRequired()])
    submit = SubmitField('Submit')

class PrescriptionForm(FlaskForm):
    patient = SelectField('Patient', choices=[], validators=[InputRequired()])
    medicine = StringField('Medicine', validators=[InputRequired()])
    dosage = TextAreaField('Dosage', validators=[InputRequired(),Length(max=2048)])
    disease = StringField('Disease', validators=[InputRequired()])
    submit = SubmitField("Create prescription")


#confirming appointment
class AppointmentConfirmForm(FlaskForm):
    #default date for appointment booking is tomorrow
    appdate = DateField('Date:',format='%Y-%m-%d',validators=[DataRequired()])
    apptime = TimeField('Time:',format='%H:%M',validators=[DataRequired()])
    approom = StringField('Room:',validators=[DataRequired(),Length(min=1,max=4)])
    submit = SubmitField('Confirm')
    
    #checks if appointment has been booked before today
    def validate_appdate(self,appdate):
        if (appdate.data) <= date.today():
            print('ok')
            raise ValidationError('Appointment cannot be booked in the past.')

class AppointmentFollowUpForm(FlaskForm):
    fulfilled = BooleanField('Did the patient attend the appointment?')
    patient_feedback = TextAreaField('Follow-up notes for patient',validators=[InputRequired(),Length(max=1024)])        
    doctor_notes = TextAreaField('Doctor notes',validators=[InputRequired(),Length(max=2048)])
    submit = SubmitField('Confirm')

class updateForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(),Length(min=3,max=32),Email()])
    houseNo = StringField('House number',validators=[InputRequired(),Length(max=5)])
    streetName = StringField('Street name',validators=[InputRequired(),Length(min=3,max=32)])
    postcode = StringField('Postcode',validators=[InputRequired(),Length(min=5,max=7)])
    submit = SubmitField("Register")

class patientRegistrationForm(FlaskForm):
    NHSNumber = StringField('NHS Number', validators=[InputRequired(),Length(min=10,max=10)])
    dob = DateField('Date of birth',format='%Y-%m-%d',validators=[InputRequired()])
    birth_sex = SelectField('Birth sex',choices=[('M'),('F')],validators=[DataRequired()])
    forename = StringField('Forename',validators=[InputRequired()])
    surname = StringField('Surname',validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(),Length(min=3,max=32),Email()])
    weight = FloatField('Weight',validators=[InputRequired(),NumberRange(min=0.0,max=500.0)])
    houseNo = StringField('House number',validators=[InputRequired(),Length(max=5)])
    streetName = StringField('Street name',validators=[InputRequired(),Length(min=3,max=32)])
    postcode = StringField('Postcode',validators=[InputRequired(),Length(min=5,max=7)])
    password = PasswordField('Password', validators=[InputRequired(),Length(min=8,max=80)])
    password2 = PasswordField('Repeat password',validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField("Register")

    def validateNHSNumber(self, NHSNumber):
        try:
            int(NHSNumber)
        except:
            raise ValidationError("NHS Number is not a number.")
        user = Patient.query.filter_by(NHSNumber=NHSNumber.data).first()
        if user is not None:
            raise ValidationError("NHS Number already in use.")
    
    def validateEmail(self, email):
        user = Patient.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Email already in use.")

#example for user creation
class doctorRegistrationForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(),Length(min=3,max=32),Email()])
    accessLev = SelectField('Access Level',default=2,choices=[(1),(2),(3)])
    NINumber = StringField('NI Number', validators=[InputRequired(),Length(min=9,max=9)])
    forename = StringField('Forename',validators=[InputRequired()])
    surname = StringField('Surname',validators=[InputRequired()])
    gender = SelectField('Gender',choices=[('M'),('F'),('O')],validators=[DataRequired()])
    dob = DateField('Date of birth',format='%Y-%m-%d',validators=[InputRequired()])
    houseNo = StringField('House number',validators=[InputRequired(),Length(max=5)])
    streetName = StringField('Street name',validators=[InputRequired(),Length(min=3,max=32)])
    postcode = StringField('Postcode',validators=[InputRequired(),Length(min=5,max=7)])
    password = PasswordField('Password', validators=[InputRequired(),Length(min=8,max=80)])
    password2 = PasswordField('Repeat password',validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField("Register")
    
    def validate_email(self,email):
        user = Doctor.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Email already in use.")

    def validate_NINumber(self,NINumber):
        user = Doctor.query.filter_by(NINumber=NINumber.data).first()
        if user is not None:
            raise ValidationError("NI Number already in use.")
        
class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class ReferralForm(FlaskForm):
    disease = StringField('Disease',validators=[InputRequired()])
    refDate = DateField('Date of referral',validators=[InputRequired()])
    refType = StringField('Type of referral',validators=[InputRequired()])
    ref_notes = TextAreaField('Referral notes',validators=[InputRequired(),Length(max=2048)])
    submit = SubmitField('Add referral')

class TestForm(FlaskForm):
    testDate = DateField('Date of test',validators=[DataRequired()])
    patient = SelectField('Patient', choices=[], validators=[DataRequired()])
    testType = StringField('Type of test',validators=[InputRequired()])
    test_notes = TextAreaField('Doctor notes',validators=[InputRequired(),Length(max=2048)])
    submit = SubmitField('Log test')

class SearchForm(FlaskForm):
    NHSNumber = StringField('NHS Number', validators=[InputRequired(),Length(min=10,max=10)])
    submit = SubmitField('Search')

    def validate_NHSNumber(self,NHSNumber):
        user = Patient.query.filter_by(NHSNumber=int(NHSNumber.data)).first()
        if user is None:
            raise ValidationError("NHS Number not attached to a user.")
        
class IllnessForm(FlaskForm):
    #nhs number included separately
    disease=StringField('Disease',validators=[InputRequired()])
    diagDate = DateField('Date of diagnosis',validators=[InputRequired()])
    endDate = DateField('Date illness is confirmed to have ended',validators=[])
    notes=TextAreaField('Doctor notes',validators=[InputRequired(),Length(max=2048)])
    submit = SubmitField('Log illness')

    def validate_diagDate(self,diagDate):
        if (diagDate.data) > date.today():
            raise ValidationError("Date cannot be in the future.")
        