from datetime import time
from peewee import *

from _config import DEBUG

if DEBUG:
    mydb = SqliteDatabase(':memory:')
else:
    mydb = SqliteDatabase("other.db")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# CLASSES 
# from vars import Person, Heart, Brain, Place, Step, Look
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

class BaseModel(Model):
    class Meta:
        database = mydb

class Person(BaseModel):
    name = CharField()

    def get_mytimepoints(self):
        return self.timepoints

    def get_myheartbeats(self):
        return self.heartbeats

class Heart(BaseModel):
    actor = ForeignKeyField(Person, backref='heartbeats')
    timestamp = IntegerField()
    bpm = IntegerField()

    
class Brain(BaseModel):
    actor = ForeignKeyField(Person, backref='shoppingurls')
    timestamp = IntegerField()
    urls = []
    
# class Eyes(BaseModel):
#     actor = ForeignKeyField(Person, backref='streetviews')
#     timestamp = IntegerField()
# 
#     streetviews = []
#     
# class Legs(BaseModel):
#     actor = ForeignKeyField(Person, backref='steps')
#     timestamp = IntegerField()
# 
#     steps = []
    
class Place(BaseModel):
    actor = ForeignKeyField(Person, backref='timepoints')
    timestamp = IntegerField()
    point = CharField()
    mode = CharField()

    def __repr__(self):
        return self.timestamp, self.mode, loads(self.point)

class Step(BaseModel):
    # do we count steps individually
    # or count them in a 24 hour period?
    actor = ForeignKeyField(Person, backref='steps')
    steps = IntegerField()
    timestamp = IntegerField()


class Look(BaseModel):
    # do we count steps individually
    # or count them in a 24 hour period?
    actor = ForeignKeyField(Person, backref='looks')
    look = CharField()
    link = CharField()
    # timestamp = IntegerField()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# VARIABLES 
# from vars import heartratedata, sleepdata, timepointdata, stepdata, lookdata
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

heartratedata = "data/heartrate.json"
# this is 24 hours of heart-rate sampled on average every 2.76 seconds
# time has the format "19:14:00" "%H:%M:%S"
# appears to be UTC/GMT! Do we wnt to transform to local time? YES

# [{
#   "time" : "08:00:07",
#   "value" : {
#     "bpm" : 78,
#     "confidence" : 2
#   }
# }

sleepdata = "data/sleep.json"

lookdata = "data/amazon.csv"


timepointdata = "data/locations.csv"
# Start Time,End Time,Name,Latitude,Longitude
# lat/lng has been transformed and spoofed for Northern CA
# ten days were compressed into one for variety. 

stepdata = "data/steps_monday.json"
# datetime has the format "Tue 19:14:00" "%a %H:%M:%S"
# appears to be UTC/GMT

# [{
#   "dateTime" : "Sat 08:03:00",
#   "value" : "0"
# },


