from app import app, db
from app.models import Doctor, HoursSpent, Address, Allergen, Allergy, Appointment, Patient, Prescription, Disease, Medicine
from datetime import datetime, date, time
from app.numberGen import nhsgen, insurancegen, findAge, heightGen, bloodGen

#file is run from here

#always imports these when running flask app in shell
@app.shell_context_processor
def make_shell_context():
    return {"db": db, "Doctor": Doctor, "Hours": HoursSpent,
            "datetime": datetime, "date": date, "time": time,
            "Disease": Disease, "Patient": Patient, "Address": Address,
            "bloodType": bloodGen, 'nhsgen': nhsgen, 'heightGen': heightGen}