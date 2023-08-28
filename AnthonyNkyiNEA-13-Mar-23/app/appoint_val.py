from app import app, db
from app.models import Appointment, HoursSpent
from datetime import datetime, date, time, timedelta
from app.sql_connect import DB_Execute
from app.query_count import queryCount
 
def accTimeSpent(doctor_id, day):
    #calculates how much time was spent by a doctor on one day
    q1=Appointment.query.filter_by(appdate=day,doctor_id=doctor_id).order_by(Appointment.apptime.asc()) #day in format date(yyyy,mm,dd)
    timeSpent = timedelta(minutes=0)    
    length=queryCount(q1)
    print(length, "appointments on", day,"\n")
    if length > 0:
        start=q1[0].apptime
        end=q1[length-1].apptime
        print("First appointment at",start,"last appointment at",end)
        for x in range (length):
            #for each appointment 15 minutes is added
            timeSpent += timedelta(minutes=15)
            appt_time = datetime.combine(q1[x].appdate,q1[x].apptime)
            try:
                nextappt_time = datetime.combine(q1[x+1].appdate,q1[x+1].apptime)
                #is gap between appointments longer than an hour?
                if (nextappt_time-(appt_time+ timedelta(minutes=15))) > (timedelta(hours=1)):
                    timeSpent += timedelta(hours=1)
                else:
                    timeSpent+=((nextappt_time-appt_time)-timedelta(minutes=15))     
            except:
                pass
        #adds to db
        if HoursSpent.query.filter_by(doctor_id=doctor_id,date=day,leaveTime=end).first() is None:
            x=HoursSpent(doctor_id=doctor_id,date=day,entryTime=start,leaveTime=end)
            db.session.add(x)
            db.session.commit()
            print('added today\'s record to db')
    print(f"time spent on {day}:",timeSpent,"\n")
    return timeSpent

def checkOvertime(doctor_id, accessLev, appt_date=date.today()):#returns false if overtime limit exceeded
    todayTimeSpent = accTimeSpent(doctor_id,appt_date)
    print("Max time allowed on one day for level",accessLev,"doctor:", timedelta(hours=(12-accessLev)),"\n")
    if todayTimeSpent > timedelta(hours=(12-accessLev)): #higher access level / status means more time is usually spent at the surgery
        print("Recommended daily hours spent at surgery exceeded.")
        return True 
        #user doctor proceeds to input whether they want to continue booking appointment
    day=appt_date-timedelta(days=6)
    totalTimeSpent = todayTimeSpent
    while day != appt_date:
        #accumulating time spent over the past week including today
        totalTimeSpent += accTimeSpent(doctor_id, day)
        day+=timedelta(days=1)
    print("\ntotal time spent over past 7 days is",totalTimeSpent)
    print("total time allowed",timedelta(hours=(((11-accessLev)*5)-2)))
    if totalTimeSpent > timedelta(hours=(((11-accessLev)*5)-2)):
        print("Recommended weekly hours spent at surgery exceeded.")
        return True
    return False

#checks for same day clashes - 15 minute margin
def checkSlotFree(doctor_id: int, day: date, apptime: time, room):
    before=datetime.combine(day,apptime)-timedelta(minutes=15)
    print(before)
    after=datetime.combine(day,apptime)+timedelta(minutes=15)
    print(after)
    q=DB_Execute('app.db')
    #searches for appointments same day with either 
    query1=q.select(f'SELECT apptime FROM Appointment WHERE appdate="{day}" AND (doctor_id="{doctor_id}" OR room="{room}")')
    print(query1)
    if query1 is not None:
        for record in query1:
            #converting each query result to a python-readable time format
            time_obj= datetime.strptime(query1[0][0][:5], '%H:%M').time()
            print("time obj", time_obj)
            record_time=datetime.combine(day,time_obj)
            if (record_time > before) and (record_time < after):
                return False, f"You and/or room {room} are not free at {apptime} on {day}."            
    return True, f"Room {room} and doctor are free at {apptime} on {day}."