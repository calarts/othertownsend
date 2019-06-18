import random
from datetime import datetime
import json, csv

from shapely.geometry import Point
from shapely.wkt import dumps, loads

from models import Person, Heart, Place, Step, Look, Conversation
from vars import heartratedata, sleepdata, timepointdata, stepdata, lookdata

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Utils 
# from utils import gimmeLongLat, gimmeGeojson, gimmeSeconds, random_line
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# from Knuth...
def random_line(afile):
    line = next(afile)
    for num, aline in enumerate(afile, 2):
        if random.randrange(num): continue
        line = aline
    return line

# Get a line: 
# with open("data/townsendtalk.txt") as f:
#     print(random_line(f))

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
    

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Build the Tables 
# from utils import createPersondb, createHeartdb, createPlacedb, createStepdb, CreateLookdb, createConversationdb
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def createPersondb(mydb):
    try:
        other = Person.get(name='OTHER')
        created = False
    except:
        mydb.create_tables([Person])
        other = Person.create(
        	name='OTHER',
        	telegram_id=123456789,
        	created_at=datetime.now(),
        	chat_name='othertownsend',
        	first_name='Other',
        	last_name="Townsend",
        	login="othertownsend",
        	language_code="en"
        	)
        created = True

# 	telegram_id = BigIntegerField()
# 	created_at = DateTimeField()
# 	chat_name = CharField()
# 	first_name = CharField()
# 	last_name = CharField()
# 	login = CharField()
# 	language_code = CharField()

    
    print("Person table is ready and 'OTHER' was created", created)
    return other
    
# Create the CONVERSATION table.
# Run this ONLY ONE TIME IN PRODUCTION!

def createConversationdb(mydb):
    try:
        print("The Conversation table has", len(Conversation), "entries and it's ready!")
    except:
        mydb.create_tables([Conversation])
        print("Your new Conversation table is ready")

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
                tp, created = Place.get_or_create(actor=other, 
                	timestamp=gimmeSeconds(thetime=row[0], timeadjust=-7), 
                	point=dumps(mypoint), 
                	mode="WALK")
            except:
                mydb.create_tables([Place])
                tp = Place.create(actor=other, 
                	timestamp=gimmeSeconds(thetime=row[0], timeadjust=-7), 
	                point=dumps(mypoint), 
	                mode="WALK")
                tp.save()

    print("Place table is ready and 'steps' was created", created)


def createLookdb(mydb,other):
    with open(lookdata, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        # This skips the first row of the CSV file.
        next(csvreader)
        for row in csvreader:
            look = str(row[0])
            link = str(row[1])
            try:
                mylook, created = Look.get_or_create(actor=other,look=look,link=link)
            except:
                mydb.create_tables([Look])
                mylook = Look.create(actor=other,look=look,link=link)
                mylook.save()

    print("Look table is ready and 'looks' was created", created)


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