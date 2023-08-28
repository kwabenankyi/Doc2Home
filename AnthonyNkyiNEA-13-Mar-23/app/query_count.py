from app.models import Appointment
from datetime import datetime
from app.createdClass import myQueue
from sqlalchemy import *

def createQueryQueue(query, size=10):
    queue = None
    if query != None:
        #if there are requested appointments, creates queue to store them in order of date-time ascending
        if queryCount(query) > size:
            queue = myQueue(size)
        else:
            queue = myQueue(queryCount(query))
        for i in range (queue.size):
            queue.enQueue(query[i])
    return queue

def queryCount(query):
    x=0
    try:
        for item in query:
            x+=1
    except:
        pass
    return x