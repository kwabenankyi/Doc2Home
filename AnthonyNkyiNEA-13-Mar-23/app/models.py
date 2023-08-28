from datetime import datetime, date, time
from time import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login 
from flask_login import UserMixin

class Doctor(UserMixin,db.Model):
#attributes to be added to db    
    doctor_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), index=True, unique=True)
    accessLev = db.Column(db.Integer, index=True)
    NINumber = db.Column(db.String(9), index=True, unique=True)
    forename = db.Column(db.String(30), index=True)
    surname = db.Column(db.String(50), index=True)
    gender = db.Column(db.String, index=True)
    dob = db.Column(db.Date)
    passwordHash = db.Column(db.String(128), index=True)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'))

    def setPassword(self, password):
        self.passwordHash = generate_password_hash(password)
    
    def checkPassword(self, password):
        return check_password_hash(self.passwordHash,password)

    def get_id(self):
        return (self.doctor_id)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.doctor_id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    #reset password key contained in email that is hashed for the id
    def verify_reset_password_token(token):
        try:
            doctor_id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            print("\n failure")
            return
        return Doctor.query.get(doctor_id)


    def __repr__(self):#how the object is represented when called with no function
        return '<Dr. {}. {} born {}>'.format((self.forename)[0],self.surname,self.dob)

class HoursSpent(db.Model):
    hours_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer,db.ForeignKey('doctor.doctor_id'))
    date = db.Column(db.Date)
    entryTime = db.Column(db.Time)
    leaveTime = db.Column(db.Time)

    def __repr__(self):
        return '<Doctor id {} entered the surgery at {} and left at {} on {}.'.format(self.id,self.entryTime,self.leaveTime,self.date)

class Medicine(db.Model):
    med_id = db.Column(db.Integer, primary_key=True)
    medicineName = db.Column(db.String(64), index=True, unique=True)
    recommendedDose = db.Column(db.String(128))

    def __repr__(self):
        return f'<Medicine {self.medicineName} id {self.med_id} has recommended dosage {self.recommendedDose}.'

class Disease(db.Model):
    disease_id = db.Column(db.Integer, primary_key=True)
    diseaseName = db.Column(db.String(128), index=True)
    inheritability = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Disease {self.diseaseName} id {self.disease_id} has inheritability status {self.inheritability}.'

class Allergen(db.Model):
    allergen_id = db.Column(db.Integer, primary_key=True)
    allergenName = db.Column(db.String(128), unique=True)

    def __repr__(self):
        return f'< {self.allergenName} >'

class Patient(UserMixin,db.Model):
    NHSNumber = db.Column(db.Integer, primary_key=True)
    forename = db.Column(db.String(30), index=True)
    surname = db.Column(db.String(50), index=True)
    email = db.Column(db.String(50), index=True, unique=True)
    dob = db.Column(db.Date, index=True)
    sex = db.Column(db.String(1), index=True)
    height = db.Column(db.Integer, index=True)#randomised
    weight = db.Column(db.Float, index=True)
    bloodType = db.Column(db.String(3), index=True)#randomised
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'))
    passwordHash = db.Column(db.String(128), index=True)

    def setPassword(self, password):
        self.passwordHash = generate_password_hash(password)
    
    def checkPassword(self, password):
        return check_password_hash(self.passwordHash,password)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.NHSNumber, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            NHSNumber = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return Patient.query.get(NHSNumber)

    def get_id(self):
        return (self.NHSNumber)

#address in separate table for speed purposes + because multiple individuals may live in the same address
class Address(db.Model):
    address_id = db.Column(db.Integer, primary_key=True)
    houseNo = db.Column(db.String(5))
    streetName = db.Column(db.String(36), index=True)
    postcode = db.Column(db.String(7), index=True)

    def __repr__(self):
        return f'<{self.houseNo} {self.streetName}, {self.postcode}.>'

    def search(self, houseNumber, street, post_code):
        #searches for address passed as parameter
        address = Address.query.filter_by(houseNo=(houseNumber.lower()),streetName=(street.upper()),postcode=(post_code.upper())).first()
        if address is None: #if address has not been found, it is added to database
            address = Address(houseNo=(houseNumber.lower()),streetName=(street.upper()),postcode=(post_code.upper()))
            db.session.add(address)
            db.session.commit()
        return address.address_id

#medicines that contain a potential allergen
class Ingredient(db.Model):
    ingredient_id = db.Column(db.Integer, primary_key=True)
    med_id = db.Column(db.Integer, db.ForeignKey('medicine.med_id'))
    allergen_id = db.Column(db.Integer, db.ForeignKey('allergen.allergen_id'))

#carrier of inheritable disease
class Carrier(db.Model):
    carrier_id = db.Column(db.Integer, primary_key=True)
    NHSNumber = db.Column(db.Integer, db.ForeignKey('patient.NHSNumber'))
    disease_id = db.Column(db.Integer, db.ForeignKey('disease.disease_id'))

    def __repr__(self) -> str:
        return f"< {Disease.query.filter_by(disease_id=self.disease_id).first().diseaseName} >"

class Allergy(db.Model):
    patientAllergy_id = db.Column(db.Integer, primary_key=True)
    NHSNumber = db.Column(db.Integer, db.ForeignKey('patient.NHSNumber'))
    allergen_id = db.Column(db.Integer, db.ForeignKey('allergen.allergen_id'))
    severity = db.Column(db.Integer, default=1)#severity of allergy from extreme to minimal (1-5)

    def __repr__(self):
        return f"< {Allergen.query.filter_by(allergen_id=self.allergen_id).first().allergenName} >"

class Prescription(db.Model):
    prescription_id = db.Column(db.Integer, primary_key=True)
    med_id = db.Column(db.Integer, db.ForeignKey('medicine.med_id'))
    NHSNumber = db.Column(db.Integer, db.ForeignKey('patient.NHSNumber'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'))
    disease_id = db.Column(db.Integer, db.ForeignKey('disease.disease_id'))
    startDate = db.Column(db.Date, index=True)
    dose = db.Column(db.String(2048))
    finalRepeatDate = db.Column(db.Date, index=True)

    def __repr__(self):
        return f"< Prescription {self.prescription_id} for {Disease.query.filter_by(disease_id=self.disease_id).first().diseaseName} started {self.startDate} >"

class Appointment(db.Model):
    appointment_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer,db.ForeignKey('doctor.doctor_id'))
    NHSNumber = db.Column(db.Integer,db.ForeignKey('patient.NHSNumber'))
    appdate = db.Column(db.Date, index=True)
    apptime = db.Column(db.Time, index=True)    
    room = db.Column(db.String(64))
    fulfilled = db.Column(db.Boolean, default=False)
    patient_feedback = db.Column(db.String(1024))#
    doctorNotes = db.Column(db.String(2048))

    def __repr__(self):
        return f'Appointment {self.appointment_id} date {self.appdate} time {self.apptime} in room {self.room}.'

class Test(db.Model):
    test_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer,db.ForeignKey('doctor.doctor_id'))
    NHSNumber = db.Column(db.Integer,db.ForeignKey('patient.NHSNumber'))    
    testDate = db.Column(db.Date, index=True)
    testType = db.Column(db.String(64), index=True)
    testDoctorNotes = db.Column(db.String(2048))

#illnesshistory
class IllnessHistory(db.Model):
    unhealthy_id = db.Column(db.Integer, primary_key=True)
    NHSNumber = db.Column(db.Integer,db.ForeignKey('patient.NHSNumber'))    
    disease_id = db.Column(db.Integer, db.ForeignKey('disease.disease_id'))
    diagnosisDate = db.Column(db.Date, index=True)
    endDate = db.Column(db.Date, index=True)
    notes = db.Column(db.String(4096))

    def __repr__(self):
        if self.endDate is None:
            return f'< Became ill with disease {Disease.query.filter_by(disease_id=self.disease_id).first().diseaseName} on {self.diagnosisDate} >'
        else:
            return f'< Became ill with disease {Disease.query.filter_by(disease_id=self.disease_id).first().diseaseName} on {self.diagnosisDate} and healed fully on {self.endDate} >'

class Referral(db.Model):
    referral_id = db.Column(db.Integer, primary_key=True)
    NHSNumber = db.Column(db.Integer, db.ForeignKey('patient.NHSNumber'))
    disease_id = db.Column(db.Integer, db.ForeignKey('disease.disease_id'))   
    diagnosisDate = db.Column(db.Date, index=True)  
    type = db.Column(db.String(64), index=True)       
    notes = db.Column(db.String(2048))
    
    def __repr__(self):
        return f"< Referral of type {self.type} for disease {Disease.query.filter_by(disease_id=self.disease_id).first().diseaseName} took place on {self.diagnosisDate}. >"

@login.user_loader  
def load_user(id):
    #searches for doctor/patient in database using 
    if Patient.query.get(int(id)) != None:
        return Patient.query.get(int(id))
    else:
        return Doctor.query.get(int(id))