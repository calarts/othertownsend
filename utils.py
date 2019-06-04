from datetime import datetime
import json, csv

from shapely.geometry import Point
from shapely.wkt import dumps, loads

from vars import Person, Heart, Brain, Place, Step
from vars import heartratedata, sleepdata, timepointdata, stepdata

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Utils 
# from utils import gimmeLongLat, gimmeGeojson, gimmeSeconds, gimmecurseconds, gimmeclosestkv, gimmecurrsteps, gimmeclosestplace
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def gimmeFeelings(myday=int(datetime.today().day)):
    feels = ["💛","💜","💜","💛","💜","💜","💛",
        "💛","💛","💛","💛","💛","💜","💜",
        "💛","💜","💜","💛","💛","💜","💛",
        "💜","💛","💛","💜","💜","💛","💛",
        "💜","💛","💛","💛","💜","💛","💜"]
    sleeps = ["➖","〰️","➖","➖","➖","➖","〰️",
        "➖","〰️","➖","〰️","➖","➖","➖",
        "➖","➖","➖","〰️","➖","➖","➖",
        "➖","➖","➖","➖","〰️","➖","〰️",
        "➖","〰️","➖","➖","➖","➖","➖"]
    return feels[myday], sleeps[myday]

def gimmeLongLat(stups):
    # ugh, must reverse lat and lng
    revtups = []
    for tup in stups:
        revtups.append(tup[::-1])
    return revtups

def gimmeGeojson(atrip,myloc):
    feature_collection = []
    # ugh, must reverse lat and lng
    revtups = gimmeLongLat(atrip)
    myline = LineString(revtups)
    mylocrev = Point( gimmeLongLat([myloc])[0] )
    mylocrevfeature = Feature(geometry=mylocrev,name="my current point")
    mylinefeature = Feature(geometry=myline,name="my trip")
    feature_collection = [mylocrevfeature,mylinefeature]
    myfeaturecollection = FeatureCollection(feature_collection)
    return myfeaturecollection


def gimmeSeconds(thetime="08:02:02", thefmt="%H:%M:%S", timeadjust=0):
    s = datetime.strptime(thetime, thefmt).second * 1
    ms = datetime.strptime(thetime, thefmt).minute * 60
    hs = datetime.strptime(thetime, thefmt).hour * 3600

    if (timeadjust != 0):
        # timeadjust is set in hours
        correction = (timeadjust*360)
        utcsecs = int(s+ms+hs)
        # LAX is 7 hours behind UTC, -2520 seconds
        localsecs = (utcsecs-correction)% 86400
    else:
        localsecs = int(s+ms+hs)

    return int(localsecs)

def gimmecurseconds():
    now = datetime.now()     # should be local time!
    secs_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return int(secs_since_midnight)

def gimmeclosestkv(mykeys):
#     mykeys = set().union(*(d.keys() for d in alistofdicts))
    mykey = min(mykeys, key=lambda x:abs(x - gimmecurseconds() ))
    q = Heart.select().where(Heart.timestamp == int(mykey))
    for entry in q:
        mybpm = entry.bpm    

    return mykey,mybpm

def gimmebeats(mykeys):
#     mykeys = set().union(*(d.keys() for d in alistofdicts))
    mykey = min(mykeys, key=lambda x:abs(x - gimmecurseconds() ))
    q = Heart.select().where(Heart.timestamp == int(mykey))
    for entry in q:
        mybpm = entry.bpm    

    return mybpm

def gimmecurrsteps(mykeys):
    mykey = min(mykeys, key=lambda x:abs(x - gimmecurseconds() ))
    q = Step.select().where(Step.timestamp == int(mykey))
    for entry in q:
        mysteps = entry.steps    

    return mykey,mysteps

def gimmeclosestplace():
#     mykeys = set().union(*(d.keys() for d in alistofdicts))
    # get the keys by querying the places
    mykeys = []
    q = Place.select()
    for entry in q:
        mykeys.append(int(entry.timestamp))

    mykey = min(mykeys, key=lambda x:abs(x - gimmecurseconds() ))

    q = Place.select().where(Place.timestamp == int(mykey))
    for entry in q:
        myplce = entry.point

    return mykey,myplce
    

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Build the Tables 
# from utils import createPersondb, createHeartdb, createPlacedb, createStepdb
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def createPersondb(mydb):
    try:
        other, created = Person.get_or_create(name='OTHER')
    except:
        mydb.create_tables([Person])
        other, created = Person.get_or_create(name='OTHER')

    
    print("Person table is ready and 'OTHER' was created", created)
    return other
    
# Create the HEART table.
# Run this ONLY ONCE IN PRODUCTION!

def createHeartdb(mydb,other):
    with open(heartratedata, 'r') as f:
        json_text = f.read()

    heartrate_list = json.loads(json_text)

    for rec in heartrate_list:
        secs = gimmeSeconds(thetime=rec['time'], thefmt="%H:%M:%S", timeadjust=-7)
        bpm = rec['value']['bpm']

        try:
            beats, created = Heart.get_or_create(actor=other, timestamp=secs, bpm=bpm)
        except:
            mydb.create_tables([Heart])
            beats = Heart.create(actor=other, timestamp=secs, bpm=bpm)
            beats.save()
        
    print("Heart table is ready and 'beats' was created", created)


def createPlacedb(mydb,other):
    with open(timepointdata, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        # This skips the first row of the CSV file.
        next(csvreader)
        for row in csvreader:
            mypoint = Point(float(row[3]), float(row[4]))
            try:
                tp, created = Place.get_or_create(actor=other, timestamp=gimmeSeconds(thetime=row[0], timeadjust=-7), point=dumps(mypoint), mode="WALK")
            except:
                mydb.create_tables([Place])
                tp = Place.create(actor=other, timestamp=gimmeSeconds(thetime=row[0], timeadjust=-7), point=dumps(mypoint), mode="WALK")
                tp.save()

    print("Place table is ready and 'steps' was created", created)


def createStepdb(mydb,other):
    with open(stepdata, 'r') as f:
        json_text = f.read()

    step_list = json.loads(json_text)

    for rec in step_list:
        secs = gimmeSeconds(rec['dateTime'], thefmt="%a %H:%M:%S", timeadjust=0)
        val = rec['value']

        try:
            steps, created = Step.get_or_create(actor=other, timestamp=secs, steps=val)
        except:
            mydb.create_tables([Step])
            steps = Step.create(actor=other, timestamp=secs, steps=val)
            steps.save()
        
    print("Step table is ready and 'steps' was created", created)