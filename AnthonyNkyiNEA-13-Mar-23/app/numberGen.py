from random import randint, choice
from string import ascii_uppercase
from datetime import date, time, datetime
import numpy as np

#mean height- age:height(cm)
MEDIAN_M_HEIGHT = {0:50,1:77,2:87,3:96,4:103,5:110,6:116,7:122,8:128,9:133,10:137,11:143,12:148,13:155,14:162,15:169,16:173,17:176,'adult':175.3}
MEDIAN_F_HEIGHT = {0:49,1:74,2:86,3:95,4:102,5:109,6:115,7:121,8:127,9:133,10:139,11:144,12:150,13:155,14:160,15:162,16:163,17:163,'adult':161.9}
#Standard deviation under-18 height - age:cm
SD_M_HEIGHT = {0:1.87,1:2.37,2:3.08,3:4.03,4:4.34,5:4.61,6:4.94,7:5.36,8:5.86,9:6.38,10:6.88,11:7.30,12:7.58,13:7.72,14:7.70,15:7.55,16:7.34,17:7.11,'adult':7.42}
SD_F_HEIGHT = {0:1.88,1:2.58,2:3.24,3:4.09,4:4.53,5:4.91,6:5.33,7:5.79,8:6.26,9:6.67,10:6.97,11:7.12,12:7.11,13:6.97,14:6.76,15:6.55,16:6.41,17:6.39,'adult':7.11}

def checkPatient(user):
    try:
        if user.NHSNumber is not None:
            return True
    except:
        return False

def findAge(birthdate):
    today = date.today()
    #is birthday's calendar date before today's?
    beforeToday = ((today.month, today.day) < (birthdate.month, birthdate.day))
    year_difference = today.year - birthdate.year
    age = year_difference - beforeToday
    return age

def heightGen(age,sex):
    if sex.upper() == ('M' or 'MALE'):
        if age < 18:
            mu = MEDIAN_M_HEIGHT[age]
            sigma = SD_M_HEIGHT[age]
        else:
            mu = MEDIAN_M_HEIGHT['adult']
            sigma = SD_M_HEIGHT['adult']
        height = np.random.normal(loc=mu,scale=sigma)
        return height
    elif sex.upper() == ("F" or "FEMALE"):
        if age < 18:
            mu = MEDIAN_F_HEIGHT[age]
            sigma = SD_F_HEIGHT[age]
        else:
            mu = MEDIAN_F_HEIGHT['adult']
            sigma = SD_F_HEIGHT['adult']
        height = np.random.normal(loc=mu,scale=sigma)
        return height
    else:
        return -1

def nhsgen():
    number = randint(1000000000,9999999999)
    return number

def insurancegen():
    #valid characters for each part of the NI number
    array1 = ['A','B','C','E','G','H','J','K','L','M','N','O','P','R','S','T','W','X','Y','Z']
    array2 = ['A','B','C','E','G','H','J','K','L','M','N','P','R','S','T','W','X','Y','Z']
    array3 = ['A','B','C','D']
    number = ''
    number = choice(array1)
    number += choice(array2)
    #first two letters of NI Number cannot be in given array
    while number in ['GB','BG','NK','KN','TN','NT','ZZ']:
        number = choice(array1)
        number += choice(array2)
    #middle part of NI number
    number += str(randint(100000,999999))
    #final letter of NI number
    number += choice(array3)
    return number

def bloodGen():
    bloodTypeArr = ['O+','O-','A+','A-','B+','B-','AB+','AB-']
    #random choice of weighted probabilities
    x=np.random.choice(bloodTypeArr, size=1, p=[(0.35/0.99),(0.13/0.99),(0.3/0.99),(0.08/0.99),(0.08/0.99),(0.02/0.99),(0.02/0.99),(0.01/0.99)])
    x=str(x)
    x=x[2:len(x)-2]
    return str(x)