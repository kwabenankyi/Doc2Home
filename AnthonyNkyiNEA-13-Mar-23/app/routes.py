from datetime import date, datetime
from time import localtime
from flask import render_template, flash, redirect, url_for, request, json
from flask_login import current_user, login_user, logout_user
from app import app, db
from app.forms import *
from app.email import sendPasswordResetEmail
from app.models import *
from app.appoint_val import checkOvertime, checkSlotFree
from app.createdClass import myQueue, HiddenValues
from app.numberGen import bloodGen, checkPatient, heightGen, findAge
from app.query_count import createQueryQueue, queryCount
from flask_login import login_required
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
from app.sql_connect import DB_Execute

GENDERS = ['M','F','O']
ACCESSLEV = [1,2,3]

def recent_apps(doctorID):
    #searches for all appointments with the given doctor that take place after 7 days age - recent appointments
    recent_apps = (Appointment.query.filter(Appointment.doctor_id==doctorID,Appointment.appdate>=(date.today()-timedelta(days=7)))).order_by(Appointment.appdate.desc())
    if recent_apps is not None:
        choices=[]
        for item in recent_apps:
            #gets name for each user
            forename=Patient.query.filter_by(NHSNumber=item.NHSNumber).first().forename
            surname=Patient.query.filter_by(NHSNumber=item.NHSNumber).first().surname
            if (item.NHSNumber, (forename +' '+ surname)) not in choices:#no duplicates
                choices.append((item.NHSNumber, (forename +' '+ surname)))
        return choices

#homepage
@login_required
@app.route('/')
def index():
    try:
        isP=checkPatient(current_user) #is user a patient?
        if isP==False:
            #appointments not yet fulfilled
            app=Appointment.query.filter_by(doctor_id=current_user.doctor_id,fulfilled=False).order_by(Appointment.appdate.asc(),Appointment.apptime.asc())
            arr=createQueryQueue(app)

            today=date.today().strftime("%Y-%m-%d")
            timenow=datetime.now().strftime("%H:%M")
            q=DB_Execute('app.db') 

            #get appointments that have been attended but have not had notes added for
            query1=q.select(f"SELECT * FROM Appointment WHERE (fulfilled=True AND (doctorNotes or patient_feedback IS NULL)) and (appdate<'{today}' OR (appdate='{today}' and apptime<'{timenow}'))")
            if query1 is not None:
                app_no_notes=[]
                for item in query1:
                    app_no_notes.append(item)

            return render_template('index.html',title="Titlepage",isP=isP,nextapp=arr.queue,Med=Medicine,Pat=Patient,app_no_notes=app_no_notes,today=date.today())
        elif isP==True:
            #gets earliest future appointment and all current prescriptions that have not been ended yet
            next_app=Appointment.query.filter(Appointment.NHSNumber==current_user.NHSNumber,Appointment.fulfilled==False,Appointment.appdate>=date.today()).order_by(Appointment.appdate.desc()).first()
            current_pres=Prescription.query.filter(Prescription.NHSNumber==current_user.NHSNumber,Prescription.finalRepeatDate==None)
            return render_template('index.html',title="Titlepage",isP=isP,nextapp=next_app,current_pres=current_pres,Med=Medicine,today=date.today())
    except:
        return render_template('index.html',title="Titlepage",isP=isP)


#login page
@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:#is user is already logged in?
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():#searches for user in database
        user = Doctor.query.filter_by(email=(form.email.data).lower()).first()

        if user is None or not user.checkPassword(form.password.data):
            user = Patient.query.filter_by(email=(form.email.data).lower()).first()
            if user is None or not user.checkPassword(form.password.data):            
                flash('Invalid username or password')
                return redirect(url_for('login'))

        login_user(user,remember=form.remember.data)
        #gets next page and redirects
        next_page = request.args.get('next')
        #is next page existing?
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for('index')

        return redirect(next_page)
    return render_template('loginDoc.html', title='Sign in',form=form)

#patient registration page
@app.route('/registerPatient',methods=['GET','POST'])
def registerPatient():
    if current_user.is_authenticated:#is user already logged in?
        return redirect(url_for('index'))
    form = patientRegistrationForm()
    if form.validate_on_submit():
        #additional validations
        age = findAge(form.dob.data)
        #checks if user number or email is in the database already
        userNHS = Patient.query.filter_by(NHSNumber=int(form.NHSNumber.data)).first()
        userEm = Patient.query.filter_by(email=(form.email.data).lower()).first()
        docEm = Doctor.query.filter_by(email=(form.email.data).lower()).first()
        if (userNHS or userEm or docEm) is not None:
            flash('Email or NHS number already in use.')
            return redirect(url_for('registerPatient')) 
        #ensures height generated is reasonable
        height = round(heightGen(age, (form.birth_sex.data)))
        if (height == -1) or ((age > 11) and (height < 101)):
            flash('Input error.')
            return redirect(url_for('registerPatient')) 
        
        if age < 16:
            flash('You must be 16 or over to register for this service.')
            return redirect(url_for('registerPatient'))
        bloodType = bloodGen()
        #searches for address to see if it's already stored in the address db
        x=Address()
        addressID=x.search(form.houseNo.data.upper(),form.streetName.data.upper(),form.postcode.data.upper())
        user = Patient(NHSNumber=form.NHSNumber.data,forename=form.forename.data,surname=form.surname.data,email=(form.email.data).lower(),dob=form.dob.data,sex=form.birth_sex.data,height=height,weight=form.weight.data,bloodType=bloodType,address_id=addressID)
        #hashes password then adds user
        user.setPassword(form.password.data)
        db.session.add(user)
        flash(f'{form.email.data} Registered!')
        db.session.commit()
        return redirect(url_for('login'))        
    return render_template('registerPatient.html', title='Patient registration', form=form)

#doctor registration page
@app.route('/registerDoc', methods=['GET', 'POST'])
def registerDoc():
    if current_user.is_authenticated:#user already logged in?
        return redirect(url_for('index'))
    form = doctorRegistrationForm()
    if form.validate_on_submit():
        print("searching")
        #checking for presence of email or NI number already
        userEm = Doctor.query.filter_by(email=(form.email.data).lower()).first()
        patEm = Patient.query.filter_by(email=(form.email.data).lower()).first()
        userNI = Doctor.query.filter_by(NINumber=(form.NINumber.data).upper()).first()
        if (userEm or patEm or userNI or patEm) is not None:
            flash('Email or NI number already in use.')
            return redirect(url_for('registerDoc')) 

        if form.dob.data > date(2000,1,1):
            flash('Are you sure you entered the correct birthday?')
            print('Are you sure you entered the correct birthday?')
            return redirect(url_for('registerDoc'))

        print("searching for address")
        #searching for address
        x = Address()
        addressID = x.search(form.houseNo.data.lower(),form.streetName.data.upper(),form.postcode.data.upper())
        #creating user
        user = Doctor(email=(form.email.data).lower(),accessLev=form.accessLev.data,NINumber=(form.NINumber.data).upper(),forename=form.forename.data,surname=form.surname.data,gender=form.gender.data,dob=form.dob.data,address_id=addressID)
        user.setPassword(form.password.data)

        db.session.add(user)
        flash('Registered!');print("Registered!")
        db.session.commit()
        return redirect(url_for('login'))
    else:
        print('errors',form.errors)
    return render_template('registerDoc.html', title='Doctor registration', form=form, accessLev=ACCESSLEV, genders=GENDERS)

#reset password
@app.route('/resetPasswordRequest', methods=['GET', 'POST'])
def resetPasswordRequest():
    if current_user.is_authenticated:
        flash("You must log out to reset your password.")
        return redirect(url_for('index'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        #checks to see if email is valid.
        pat = Patient.query.filter_by(email=form.email.data).first()
        doc = Doctor.query.filter_by(email=form.email.data).first()
        if pat:
            sendPasswordResetEmail(pat)
        elif doc:
            sendPasswordResetEmail(doc)
        else:
            flash('Email is not linked to an account')
            return redirect(url_for('resetPasswordRequest'))
        flash('Visit your email for the instructions to reset your password. Link expires in 10 minutes, be fast!')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/resetPassword/<token>', methods=['GET', 'POST'])
def resetPassword(token):
    if current_user.is_authenticated:
        flash("Log out to reset password")
        return redirect(url_for('index'))
    #checks to see if user id hashes to same val as token before allowing reset
    user = Patient.verify_reset_password_token(token)
    if user is None:
        user = Doctor.verify_reset_password_token(token)
    if user is None:
        print('error')
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        #checks if password is still the same
        hasnotchanged=user.checkPassword(form.password.data)
        if hasnotchanged==False:
            user.setPassword(form.password.data)
            db.session.commit()
            flash('Your password has successfully been reset.')
            return redirect(url_for('login'))
        else:
            flash("Password has not changed! Enter a new password")
    return render_template('reset_password.html', form=form, token=token)

#profile view page
@app.route('/profile/<user_id>', methods=['GET','POST'])
def viewProfile(user_id):
    try:
        all_pres=None
        allergies=None
        ill_hist=None
        inherited=None
        Ninum=None
        #is the user being viewed a doctor or patient
        user=Patient.query.filter_by(NHSNumber=int(user_id)).first()
        if user is None:
            user=Doctor.query.filter_by(doctor_id=int(user_id)).first()
            #hides ni num for security reason
            Ninum=HiddenValues(user.NINumber).hideValues(2,7)
        else:
            #gets prescriptions allergies illness history and carried diseases for profile
            all_pres=createQueryQueue(Prescription.query.filter_by(NHSNumber=user.NHSNumber).order_by(Prescription.startDate.asc()))
            allergies=createQueryQueue(Allergy.query.filter_by(NHSNumber=user.NHSNumber))
            ill_hist=createQueryQueue(IllnessHistory.query.filter_by(NHSNumber=user.NHSNumber).order_by(IllnessHistory.diagnosisDate.asc()))
            inherited=createQueryQueue(Carrier.query.filter_by(NHSNumber=user.NHSNumber))
        isP_prof=checkPatient(user)#is the profile patient or doctor?
        isP=checkPatient(current_user)#is the user viewing the profile patient or doctor?
        address = Address.query.filter_by(address_id=(user.address_id)).first()
        return render_template('profile.html',account=user,houseNo=address.houseNo, streetName=address.streetName, postcode=address.postcode,isP=isP,isP_prof=isP_prof,all_pres=all_pres,allergies=allergies,ill_hist=ill_hist,inherited=inherited,number=Ninum,spl=(len(address.postcode))-3)
    except:
        print("profile didn't work")
        flash('profile could not be loaded')
        return redirect(url_for('index'))

#update profile with email and address
@app.route('/update',methods=['GET','POST'])
def updateProfile():
    address = Address.query.filter_by(address_id=(current_user.address_id)).first()
    form=updateForm()
    #checks if patient or doctor
    if checkPatient(current_user)==False:
        updatedUser = Doctor.query.filter_by(doctor_id=current_user.doctor_id).first()
    elif checkPatient(current_user)==True:
        updatedUser = Patient.query.filter_by(NHSNumber=current_user.NHSNumber).first()
    if form.validate_on_submit():
        print('form validated')
        updatedUser.email=form.email.data
        check_add=Address.query.filter_by(houseNo=form.houseNo.data.lower(),streetName=(form.streetName.data).upper(),postcode=(form.postcode.data).upper()).first()
        #checks if address submitted has changed
        if check_add is None:
            address.houseNo=form.houseNo.data.lower()
            address.streetName=form.streetName.data.upper()
            address.postcode=form.postcode.data.upper()
        else:
            updatedUser.address_id=check_add.address_id
        #updates user and address
        db.session.commit()
        flash("Visit profile to see effected changes.")
        return redirect(url_for('index'))
    return render_template('update.html',form=form,updatedUser=updatedUser,address=address)


@app.route('/search', methods=['GET','POST'])
def search():#searches for patient by NHS number
    form=SearchForm()
    if form.validate_on_submit():
        user=Patient.query.filter_by(NHSNumber=int(form.NHSNumber.data)).first()
        return redirect(url_for('viewProfile', user_id=int(form.NHSNumber.data)))
    return render_template('search.html',isP=checkPatient(current_user),form=form)

#create appointment
@app.route('/createappointment',methods=['GET','POST'])
def createApp():
    isP = checkPatient(current_user)
    title='Book appointment'
    appointment = None
    if isP==True:#if you are a patient, you get the create-appointment form
        form = AppointmentForm()
        try:
            #gets previous appointments
            prev_app=Appointment.query.filter(Appointment.NHSNumber==current_user.NHSNumber,Appointment.fulfilled==True).order_by(Appointment.appdate.asc(),Appointment.apptime.asc())
            for item in prev_app:
                print(item)
            prev_queue=createQueryQueue(prev_app,size=99)
            print('done')
        except:
            pass
        #appointment can only be booked if they do not have an upcoming appointment
        appointment = Appointment.query.filter(Appointment.NHSNumber==current_user.NHSNumber,Appointment.fulfilled==False,Appointment.appdate>=date.today()).first()
        if appointment == None:
            if form.validate_on_submit():
                #checking if appointment doesn't clash
                appointment = Appointment(NHSNumber=current_user.NHSNumber,appdate=(form.appdate.data),apptime=(form.apptime.data))
                db.session.add(appointment)
                db.session.commit()
                print('added to db')
                return redirect(url_for('index'))
        #shows them upcoming appointment
        else:
            return render_template('appointments.html',title='Book appointment',form=form,appointment=appointment,isP=isP,prev_queue=prev_queue.queue,doc=Doctor)

    elif isP == False:# user is a doctor allowed to view appointments
        form = AppointmentConfirmForm()
        title='Requested appointments'
        doctorForm=DoctorAppointmentForm()
        doctorForm.patient.choices = [(pat.NHSNumber, (pat.forename +' '+ pat.surname)) for pat in Patient.query.all()]
        #searching for appointments that haven't been confirmed yet (i.e. no room)
        q1=Appointment.query.filter_by(room=None).order_by(Appointment.appdate.asc(),Appointment.apptime.asc()).all()
        queue1=createQueryQueue(q1)

        #searching for appointments in the past that were fulfilled and have no notes
        q2=Appointment.query.filter(Appointment.doctorNotes==None,Appointment.appdate<=date.today(),(Appointment.doctor_id==current_user.doctor_id)).order_by(Appointment.appdate.asc(),Appointment.apptime.asc())
        queue2=createQueryQueue(q2)

        #searching for appointments that are happening in the future and have been confirmed by said doctor.
        q3=Appointment.query.filter(Appointment.doctorNotes==None,(Appointment.room!=None),(Appointment.doctor_id==current_user.doctor_id)).order_by(Appointment.appdate.asc(),Appointment.apptime.asc())
        queue3=createQueryQueue(q3)

        if doctorForm.validate_on_submit():
            #checks if slot is free 
            isFree, message = checkSlotFree(current_user.doctor_id, doctorForm.appdate.data, doctorForm.apptime.data, doctorForm.approom.data)
            flash(message)
            if isFree == True:
                #creates apppointment that is only added if overtime is not exceeded
                newAppointment = Appointment(doctor_id=current_user.doctor_id,NHSNumber=(doctorForm.patient.data),appdate=doctorForm.appdate.data,apptime=doctorForm.apptime.data,room=doctorForm.approom.data)
                if checkOvertime(current_user.doctor_id,current_user.accessLev,appt_date=doctorForm.appdate.data) == True:#redirects to appointment viewer for confirmation of appointment if user is going into overtime
                    item=(Appointment.query.filter_by(doctor_id=current_user.doctor_id,NHSNumber=doctorForm.patient.data,appdate=doctorForm.appdate.data,apptime=doctorForm.apptime.data)).first()
                    forename=(Patient.query.filter_by(NHSNumber=item.NHSNumber).first()).forename
                    surname=(Patient.query.filter_by(NHSNumber=item.NHSNumber).first()).surname
                    return render_template('appointment_viewer.html',id=item.appointment_id, form=form, message="Overtime limits exceeded...",isP=isP,fn=forename,sn=surname,item=item,today=date.today(),newApp=newAppointment)
                db.session.add(newAppointment)
                db.session.commit()
                return redirect(url_for('index'))
        return render_template('appointments.html',title=title,queue1=queue1.queue,queue2=queue2.queue,queue3=queue3.queue,isP=isP,doc=Doctor,pat=Patient,form=form,doctorForm=doctorForm)
    return render_template('appointments.html',title=title,form=form,isP=isP,prev_queue=prev_queue.queue,doc=Doctor)

@app.route('/referral/<NHSNum>',methods=['GET','POST'])
def createRef(NHSNum):
    form=ReferralForm()
    #shows all previous referrals
    prev_ill=createQueryQueue(Referral.query.filter_by(NHSNumber=NHSNum).order_by(Referral.diagnosisDate.asc()),99)
    if form.validate_on_submit():
        #checks to ensure disease is in database to get id to add referral
        dis_id=Disease.query.filter_by(diseaseName=form.disease.data).first().disease_id
        ref_search=Referral.query.filter_by(NHSNumber=NHSNum,diagnosisDate=form.refDate.data,type=form.refType.data).first()
        if ref_search is None:
            new_ref=Referral(NHSNumber=NHSNum,diagnosisDate=form.refDate.data,disease_id=dis_id,type=form.refType.data,notes=form.ref_notes.data)
            db.session.add(new_ref)
            db.session.commit()
            flash('referral added')
        else:
            flash('referral already recorded')
    return render_template('referral.html',form=form,isP=checkPatient(current_user),title='Create referral',prev_ill=prev_ill.queue)

@app.route('/viewreferral/<id>',methods=['GET','POST'])
def viewRef(id):
    refer=Referral.query.filter_by(referral_id=id).first()
    allowed=True
    isP=checkPatient(current_user)
    #doctors need to have had or be having an appointment with patient in next two weeks before seeing
    if isP==False:
        if current_user.accessLev > 1:
            if (Appointment.query.filter(Appointment.appdate<=(date.today()+timedelta(days=14)),Appointment.doctor_id==current_user.doctor_id)) is None:
                allowed=False
    elif isP==True:#patients cannot view other users' referrals
        if refer.NHSNumber!=current_user.NHSNumber:
            allowed=False
    return render_template('ref_viewer.html',allowed=allowed,ref=refer,doc=Doctor,pat=Patient,id=id,isP=isP)

@app.route('/test/<appoint>',methods=['GET','POST'])
def createTest(appoint=None):#creating test linked to appointment by id
    form=TestForm()
    print(form.errors)

    NHSNum=Appointment.query.filter_by(appointment_id=appoint).first().NHSNumber
    day=Appointment.query.filter_by(appointment_id=appoint).first().appdate
    forename=Patient.query.filter_by(NHSNumber=NHSNum).first().forename
    surname=Patient.query.filter_by(NHSNumber=NHSNum).first().surname
    form.patient.choices=[(NHSNum,forename+' '+surname)]
    
    if form.validate_on_submit():
        print('sub')
        test_search=Test.query.filter_by(NHSNumber=form.patient.data,testDate=form.testDate.data,testType=form.testType.data).first()
        if test_search is None:
            print('ok')
            new_test=Test(NHSNumber=form.patient.data,testDate=form.testDate.data,doctor_id=current_user.doctor_id,testType=form.testType.data,testDoctorNotes=form.test_notes.data)
            db.session.add(new_test)
            db.session.commit()
            print('test')
            return redirect(url_for('viewApp', id=appoint))
    
    return render_template('test.html',form=form,isP=checkPatient(current_user),title='Create test',fn=forename,sn=surname,day=day,NHSNum=NHSNum)

@app.route('/viewtest/<id>',methods=['GET','POST'])
def viewTest(id):
    test=Test.query.filter_by(test_id=id).first()
    allowed=True
    isP=checkPatient(current_user)
    if isP==False:#same viewing criteria as referral
        if current_user.accessLev > 1:
            if (Appointment.query.filter(Appointment.appdate<=(date.today()+timedelta(days=14)),Appointment.doctor_id==current_user.doctor_id)) is None:
                allowed=False
    elif isP==True:
        if test.NHSNumber!=current_user.NHSNumber:
            allowed=False
    return render_template('test_viewer.html',allowed=allowed,test=test,doc=Doctor,pat=Patient,id=id,isP=isP)

@app.route('/createIllness/<NHSNum>',methods=['GET','POST'])
def createIllness(NHSNum):
    form=IllnessForm()
    allowed=False
    #previous illness history
    prev_ill=createQueryQueue(IllnessHistory.query.filter_by(NHSNumber=NHSNum).order_by(IllnessHistory.diagnosisDate.asc()),99)
    fn=Patient.query.filter_by(NHSNumber=NHSNum).first().forename
    sn=Patient.query.filter_by(NHSNumber=NHSNum).first().surname
    #gets appointments that the patient has within period four weeks ago and two weeks in the future
    four_weeks_ago=date.today()-timedelta(days=28)
    future_two_weeks=date.today()+timedelta(days=14)
    next_apps=Appointment.query.filter(Appointment.appdate>=four_weeks_ago,Appointment.appdate<=future_two_weeks,Appointment.doctor_id==current_user.doctor_id,Appointment.NHSNumber==NHSNum)

    if form.validate_on_submit():
        try:
            #checks to see if disease is in database
            dis_id=Disease.query.filter_by(diseaseName=(form.disease.data).lower()).first().disease_id
            #searches if illness has already been recorded
            u=IllnessHistory.query.filter_by(NHSNumber=NHSNum,disease_id=dis_id,diagnosisDate=(form.diagDate.data)).first()
            if u is not None:
                flash('illness has already been recorded')
            else:
                print(NHSNum)
                print(form.diagDate.data)
                new_ill=IllnessHistory(NHSNumber=NHSNum,disease_id=dis_id,diagnosisDate=(form.diagDate.data),notes=form.notes.data)
                if form.endDate.data is not None:
                    if form.endDate.data < form.diagDate.data:
                        flash('disease may not end before it has started')
                        return redirect(url_for('createIllness', NHSNum=NHSNum))
                    new_ill.endDate==form.endDate.data
                db.session.add(new_ill)
                db.session.commit()
                flash('illness added')
        except:
            flash('disease does not exist')
        return redirect(url_for('createIllness', NHSNum=NHSNum))

    if (current_user.accessLev==1) or (next_apps is not None):
        allowed=True
    return render_template('illness.html',title='Patient illness history',prev_ill=prev_ill.queue,isP=checkPatient(current_user),NHSNum=NHSNum,form=form,fn=fn,sn=sn,allowed=allowed,d=Disease) 

@app.route('/viewHist/<id>',methods=['GET','POST'])
def viewHist(id):#viewing individual illness history
    illness_hist=IllnessHistory.query.filter_by(unhealthy_id=id).first()
    allowed=True
    isP=checkPatient(current_user)
    fn=Patient.query.filter_by(NHSNumber=illness_hist.NHSNumber).first().forename
    sn=Patient.query.filter_by(NHSNumber=illness_hist.NHSNumber).first().surname
    if isP==False:
        if current_user.accessLev > 1:
            if (Appointment.query.filter(Appointment.appdate<=(date.today()+timedelta(days=14)),Appointment.doctor_id==current_user.doctor_id)) is None:
                allowed=False
    elif isP==True:
        if illness_hist.NHSNumber!=current_user.NHSNumber:
            allowed=False
    return render_template('hist_viewer.html',allowed=allowed,illness_hist=illness_hist,id=id,isP=isP,fn=fn,sn=sn)

#view appointment
@app.route('/viewapp/<id>',methods=['GET','POST'])
def viewApp(id):
    #searching for appointment details
    item=Appointment.query.filter_by(appointment_id=id).first()
    forename=(Patient.query.filter_by(NHSNumber=item.NHSNumber).first()).forename
    surname=(Patient.query.filter_by(NHSNumber=item.NHSNumber).first()).surname
    #checking for a test on that day
    #checking to see if appointment can be reviewed
    if item.patient_feedback is not None:
        #displays information rather than a form
        forename=(Doctor.query.filter_by(doctor_id=item.doctor_id).first()).forename
        surname=(Doctor.query.filter_by(doctor_id=item.doctor_id).first()).surname
        post_app=True
        #gets tests linked to appointment by date to display
        linked_test=createQueryQueue(Test.query.filter_by(doctor_id=item.doctor_id,NHSNumber=item.NHSNumber,testDate=item.appdate))
        return render_template('appointment_viewer.html',id=id,isP=checkPatient(current_user),fn=forename,sn=surname,item=item,today=date.today(),post_app=post_app,linked_test=linked_test.queue)
    else:
        form = AppointmentConfirmForm()
        followUp=AppointmentFollowUpForm()
        post_app=False  
    
    if form.validate_on_submit():
        #form checked after doctor confirms request
        if checkPatient(current_user)==False:
            #checks if slot is free, then if the user would be working overtime
            isFree, message = checkSlotFree(current_user.doctor_id, form.appdate.data, form.apptime.data, form.approom.data)
            if isFree==True:
                if checkOvertime(current_user.doctor_id,current_user.accessLev,appt_date=form.appdate.data)==True:
                    flash('Overtime limit exceeded. Choose another date.')
                    return render_template('appointment_viewer.html',id=id,isP=checkPatient(current_user),form=form,fn=forename,sn=surname,item=item,today=date.today(),followUp=followUp)
                flash(message)
                flash('appointment confirmed!')
            else:
                flash(message)
                flash('Please rebook appointment at different time or room.')
                return render_template('appointment_viewer.html',id=id,isP=checkPatient(current_user),form=form,fn=forename,sn=surname,item=item,today=date.today(),followUp=followUp)

        print('done')
        #adding the new form submitted data to the database to finially confirm
        appt = Appointment.query.filter_by(appointment_id=id).first()
        appt.appdate = form.appdate.data
        appt.apptime = form.apptime.data
        appt.room = form.approom.data
        appt.doctor_id = current_user.doctor_id
        db.session.commit()
        return redirect(url_for('createApp'))

    if followUp.validate_on_submit():
        #doctor has finished appointment and is adding the information for a patient to view
        appt=Appointment.query.filter_by(appointment_id=id).first()
        appt.fulfilled=followUp.fulfilled.data
        appt.patient_feedback=followUp.patient_feedback.data
        appt.doctorNotes=followUp.doctor_notes.data
        db.session.commit()
        return redirect(url_for('createApp'))
    
    return render_template('appointment_viewer.html',id=id,isP=checkPatient(current_user),form=form,fn=forename,sn=surname,item=item,today=date.today(),followUp=followUp)

@app.route('/cancelApp/<id>')
def cancelApp(id):#cancelling appointment through api
    Appointment.query.filter_by(appointment_id=id).delete()
    db.session.commit()
    flash("Your appointment has been deleted.")
    return redirect(url_for('index'))

#add/search for allergen
@app.route('/allergens',methods=['GET','POST'])
def createAllergen():
    indb=True
    #checks if user is level 1/2 doctor before they can add
    if (checkPatient(current_user) == False) and (current_user.accessLev < 3):
        #gets allergen name and checks in database to see if unique
        allergen_data = request.form.get('allergenName')
        if allergen_data is not None:   
            query=Allergen.query.filter_by(allergenName=(allergen_data.lower())).first()
            if query==None:
                indb=False
                new_allergen=Allergen(allergenName=(allergen_data.lower()))
                db.session.add(new_allergen)
                db.session.commit()
            return render_template('allergen.html',isP=checkPatient(current_user),indb=indb,allergen=allergen_data)
    return render_template('allergen.html',isP=checkPatient(current_user))

@app.route('/allergies/<NHSNum>',methods=['GET','POST'])
def createPatientAllergy(NHSNum):#linking allergy to patient
    form = PatientAllergyForm()
    fn=Patient.query.filter_by(NHSNumber=NHSNum).first().forename
    sn=Patient.query.filter_by(NHSNumber=NHSNum).first().surname
    if form.validate_on_submit():
        #checks for allergen id then adds
        allergen_id=(Allergen.query.filter_by(allergenName=(form.allergy.data.lower())).first()).allergen_id
        new_patallergy=Allergy(NHSNumber=NHSNum,allergen_id=allergen_id,severity=form.severity.data)
        db.session.add(new_patallergy)
        db.session.commit()
        q=DB_Execute('app.db')
        #searching the prescriptions that the patient has that contain this allergen in a medicine
        query1=q.select(f'SELECT prescription.prescription_id FROM Prescription inner JOIN Ingredient ON (Prescription.med_id=Ingredient.med_id) where (ingredient.allergen_id={allergen_id} and prescription.NHSNumber={NHSNum})')
        #removes all duplicates
        query1=list(set(query1))
        #ending these prescriptions
        if query1 is not None:
            for item in query1:
                x=Prescription.query.filter_by(prescription_id=item[0]).first()
                x.finalRepeatDate=date.today()
                flash(f'Prescription {item[0]} ended due to allergy clash')
            db.session.commit()
        flash('Allergy for patient added.')
        return redirect(url_for('viewProfile', user_id=NHSNum))

    return render_template('allergy.html',form=form,isP=checkPatient(current_user),NHSNum=NHSNum,fn=fn,sn=sn)

@app.route('/medicine',methods=['GET','POST'])
def createMedicine():#searching/adding for medicines
    if (checkPatient(current_user) == False) and (current_user.accessLev < 3):
        #gets name and dose from form
        medicine_data = request.form.get('medicineName')
        med_dosage = request.form.get('dosage')
        if medicine_data is not None:
            #checks if medicine is in database   
            query=Medicine.query.filter_by(medicineName=(medicine_data.lower())).first()
            if query==None:
                new_medicine=Medicine(medicineName=(medicine_data.lower()),recommendedDose=(med_dosage.lower()))
                db.session.add(new_medicine)
                db.session.commit()
                flash(f"{medicine_data.lower()} added to database.")
                #redirect to the link med-allergy page
                return redirect(url_for('createMedAllergy'))
            return render_template('medicine.html',isP=checkPatient(current_user),indb=True,medicine=medicine_data)
    return render_template('medicine.html',isP=checkPatient(current_user))
    
@app.route('/medicine/<name>',methods=['GET','POST'])
def viewMedicine(name):
    name=name
    allergies=[]
    med_id=Medicine.query.filter_by(medicineName=name).first()
    #searches for allergens that are linked to medicine
    q=DB_Execute('app.db')
    query1=q.select(f'SELECT Allergen.allergenName FROM Allergen, Ingredient, Medicine WHERE Allergen.allergen_id=Ingredient.allergen_id AND Ingredient.med_id=Medicine.med_id AND Medicine.medicineName="{name}"')
    if query1 is not None:#GETS LIST OF ALLERGENS INSIDE MEDICINE
        for item in query1:
            allergies.append(item[0])
    return render_template('medicine_viewer.html',isP=False,name=name,allergies=allergies)    

@app.route('/medicineAllergy',methods=['GET','POST'])
def createMedAllergy():
    form = MedicineAllergyForm()
    if form.validate_on_submit():
        indb=True
        #checks if patient is access lev 1 or 2
        if (checkPatient(current_user) == False) and (current_user.accessLev < 3):
            med_id = (Medicine.query.filter_by(medicineName=(form.medicine.data).lower()).first()).med_id
            allergen_id = (Allergen.query.filter_by(allergenName=(form.allergen.data).lower()).first()).allergen_id
            #if medicine + allergen is not stored as ingredient already
            if Ingredient.query.filter_by(med_id=med_id,allergen_id=allergen_id).first() == None:
                newIngredient = Ingredient(med_id=med_id,allergen_id=allergen_id)
                db.session.add(newIngredient)
                db.session.commit()
                indb=False
            return render_template('ingred.html',form=form,isP=checkPatient(current_user),indb=indb,medicine=form.medicine.data)
        else:
            flash("unauthorised action")
            return render_template('ingred.html',form=form,isP=checkPatient(current_user))
    return render_template("ingred.html",form=form,isP=checkPatient(current_user))
            
@app.route('/disease',methods=['GET','POST'])
def createDisease():#add disease to system
    if request.method == 'POST':
        indb=True
        disease_name = request.form.get('disease_name')
        inheritable = request.form.get('ch1')
        #checks if disease is already recorded
        query=Disease.query.filter_by(diseaseName=(disease_name.lower())).first()
        if query is None:#disease doesn't exist
            new_disease = Disease(diseaseName=(disease_name.lower()),inheritability=False)
            if inheritable is not None: #the disease is inheritable if it is ticked on
                new_disease.inheritability = True
            db.session.add(new_disease)
            db.session.commit()
            indb=False
        return render_template('disease_add.html',isP=checkPatient(current_user),indb=indb, message="Disease added", disease=disease_name)
    return render_template('disease_add.html',isP=checkPatient(current_user))

@app.route('/inheritable/<NHSNum>',methods=['GET','POST'])
def createInherit(NHSNum):#add carried disease to a patient
    if request.method == 'POST':
        indb=True
        disease_name=request.form.get('disease_name')
        #is the disease actually inheritable?
        dis_id=Disease.query.filter_by(diseaseName=disease_name,inheritability=True).first()
        if dis_id is not None:
            #has inheritable disease been recorded already
            carrier=Carrier.query.filter_by(disease_id=dis_id.disease_id,NHSNumber=NHSNum).first()
            if carrier is None:
                new_carrier=Carrier(disease_id=dis_id.disease_id,NHSNumber=NHSNum)
                db.session.add(new_carrier)
                db.session.commit()
                indb=False
                
            return render_template('carrier.html',isP=checkPatient(current_user),indb=indb,NHSNum=NHSNum,patient=Patient.query.filter_by(NHSNumber=NHSNum).first(),disease=disease_name)
        else:
            flash('Disease does not exist, enter a valid disease name')
    return render_template('carrier.html',isP=checkPatient(current_user),NHSNum=NHSNum,patient=Patient.query.filter_by(NHSNumber=NHSNum).first())

@app.route('/prescription',methods=['GET','POST'])
def createPres():#creating prescription
    if checkPatient(current_user)==False:
        form = PrescriptionForm()
        #doctor may only create prescriptions for patients he is due to interact with
        form.patient.choices=recent_apps(current_user.doctor_id)
        
        if form.validate_on_submit():
            #searching for prescription with same patient and medicine that hasn't ended yet
            medid = Medicine.query.filter_by(medicineName=form.medicine.data).first()
            disid = Disease.query.filter_by(diseaseName=form.disease.data).first()
            if (medid or disid) is None:
                flash("Disease or medicine does not exist. Ensure you have spelt the name correctly and are using the autocomplete.") 
                return render_template('prescription.html', isP=checkPatient(current_user), form=form)
            else:
                #checks if prescription already exists - if it does it is updated
                q1 = Prescription.query.filter_by(NHSNumber=form.patient.data,med_id=medid.med_id,disease_id=disid.disease_id,finalRepeatDate=None).first()
                if q1 is not None:
                    if q1.startDate == date.today():
                        q1.dose = form.dosage.data
                    else:
                        new_pres = Prescription(med_id=medid.med_id,NHSNumber=form.patient.data,doctor_id=current_user.doctor_id,disease_id=disid.disease_id,startDate=date.today(),dose=form.dosage.data)
                        q1.finalRepeatDate=date.today()
                    db.session.commit()
                    flash("Prescription updated")
                    return render_template('prescription.html', isP=checkPatient(current_user), form=form)
                else:
                    #searching illness history to see if the patient is ill and it has been recorded
                    q2=IllnessHistory.query.filter(IllnessHistory.NHSNumber==form.patient.data,IllnessHistory.disease_id==disid.disease_id,IllnessHistory.diagnosisDate<=date.today(),IllnessHistory.endDate==None).first()
                    if queryCount(q2)>0:
                        pass
                    else:
                        new_illness=IllnessHistory(NHSNumber=form.patient.data,disease_id=disid.disease_id,diagnosisDate=date.today())
                        db.session.add(new_illness)
                        db.session.commit()
                    #searching for allergens found in medicine
                    allergens_in_med = Ingredient.query.filter_by(med_id=medid.med_id)
                    for x in allergens_in_med:
                        all_id=x.allergen_id
                        #search allergy table to see if patient has the allergic reaction
                        if Allergy.query.filter_by(NHSNumber=form.patient.data,allergen_id=all_id).first() is not None:
                            flash(f"{Medicine.query.filter_by(med_id=medid.med_id).first().medicineName} contains the allergen {Allergen.query.filter_by(allergen_id=all_id).first().allergenName} and thus cannot be prescribed to the patient, due to risk of allergic reaction.")
                            return render_template('prescription.html', isP=checkPatient(current_user), form=form)
                            
                    new_pres = Prescription(med_id=medid.med_id,NHSNumber=form.patient.data,doctor_id=current_user.doctor_id,disease_id=disid.disease_id,startDate=date.today(),dose=form.dosage.data)
                    db.session.add(new_pres)
                    db.session.commit()
                    print('added pres')
                    flash('prescription added')
                    return redirect((url_for('index')))
        return render_template('prescription.html', isP=checkPatient(current_user), form=form)

@app.route('/viewPrescription/<id>',methods=['GET','POST'])
def viewPres(id):#view prescription
    pres=Prescription.query.filter_by(prescription_id=id).first()
    medName=Medicine.query.filter_by(med_id=pres.med_id).first().medicineName
    doc=Doctor.query.filter_by(doctor_id=pres.doctor_id).first()
    docName=doc.forename+' '+doc.surname
    disName=Disease.query.filter_by(disease_id=pres.disease_id).first().diseaseName
    print(disName)
    return render_template('prescription_viewer.html', isP=checkPatient(current_user), title='View Prescription',medName=medName,docName=docName,disName=disName,pres=pres)

@app.route('/api/<name>')
def api_get(name):#api returning lists for each autocompleted function
    if name == 'allergens':
        return json.jsonify({
            'allergens': [(substance.allergenName) for substance in Allergen.query.all()]
        })
    elif name == 'medicine':
        return json.jsonify({
            'medicine': [(substance.medicineName) for substance in Medicine.query.all()]
        })
    elif name == 'disease':
        return json.jsonify({
            'disease': [(substance.diseaseName) for substance in Disease.query.all()]
        })
    elif name == 'carrier':
        return json.jsonify({
            'carrier': [(substance.diseaseName) for substance in Disease.query.filter(Disease.inheritability==True)]
        })
    elif name == 'referral_type':
        if Referral.query.all() is not None:
            x={'referral_type': [(t.type) for t in Referral.query.all()]}
            for i in range (len(x['referral_type'])):
                #checks for duplicates - if the index is not the first returned then there is more than one of the value in the array
                if x['referral_type'].index(x['referral_type'][i]) != i:
                    x['referral_type'].pop(i)
        else:
            x={'referral_type': []}
        return json.jsonify(x)
    elif name == 'test_type':
        if Test.query.all() is not None:
            x={'test_type': [(t.testType) for t in Test.query.all()]}
            for i in range (len(x['test_type'])):
                #checks for duplicates - if the index is not the first returned then there is more than one of the value in the array
                if x['test_type'].index(x['test_type'][i]) != i:
                    x['test_type'].pop(i)
        else:
            x={'test_type': []}
        return json.jsonify(x)


#logging out of account
@app.route('/logout')
def logout():
    logout_user()
    print("logged out")
    return redirect(url_for('index'))