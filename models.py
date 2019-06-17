from random import choice
from datetime import time, datetime

from peewee import *

from _config import DEBUG

if DEBUG:
    mydb = SqliteDatabase(':memory:')
else:
    mydb = SqliteDatabase("other.db")



def gimmecurseconds():
    now = datetime.now()     # should be local time!
    secs_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    return int(secs_since_midnight)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# MODELS
# from models import Person, Heart, Brain, Place, Step, Look, Conversation
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


class BaseModel(Model):
    class Meta:
        database = mydb

class Person(BaseModel):
    name = CharField()
    telegram_id = BigIntegerField()
    created_at = DateTimeField()
    chat_name = CharField()
    first_name = CharField()
    last_name = CharField()
    login = CharField()
    language_code = CharField()

    def get_mytimepoints(self):
        return self.timepoints

    def get_myheartbeats(self):
        return self.heartbeats

    def get_myconversations(self):
        return self.conversations

    def get_personalreply(self,update,themeat):
        pleasentries = ['Hi',
                            'yawn',
                            'are you still here?'
                            'I was just getting back to it.',
                            'could you ask me in a few minutes?',
                            "I'll sleep when I'm dead."]
        personalreply = "Hi again " + str(update.message.from_user.name) + "!\n"
        personalreply = personalreply + choice(pleasentries)
        personalreply = personalreply + themeat
        return personalreply

    def get_mymood(self,myday=int(datetime.today().day)):
        feels = ["💛","💜","💜","💛","💜","💜","💛",
            "💛","💛","💛","💛","💛","💜","💜",
            "💛","💜","💜","💛","💛","💜","💛",
            "💜","💛","💛","💜","💜","💛","💛",
            "💜","💛","💛","💛","💜","💛","💜"]
        self.feels = feels[myday]
        if self.feels == "💜": self.mood = 0
        if self.feels == "💛": self.mood = 1
        return self.feels, self.mood

    def get_mysleep(self,myday=int(datetime.today().day)):
        sleeps = ["➖","〰️","➖","➖","➖","➖","〰️",
            "➖","〰️","➖","〰️","➖","➖","➖",
            "➖","➖","➖","〰️","➖","➖","➖",
            "➖","➖","➖","➖","〰️","➖","〰️",
            "➖","〰️","➖","➖","➖","➖","➖"]
        self.sleep = sleeps[myday]
        return self.sleep

    def gimmebeats(self,mykeys):
        # mykeys = set().union(*(d.keys() for d in alistofdicts))
        mykey = min(mykeys, key=lambda x:abs(x - gimmecurseconds() ))
        q = Heart.select().where(Heart.timestamp == int(mykey))
        for entry in q:
            self.mybpm = entry.bpm

        return self.mybpm

    def gimmecurrsteps(self,mykeys):
        mykey = min(mykeys, key=lambda x:abs(x - gimmecurseconds() ))
        q = Step.select().where(Step.timestamp == int(mykey))
        for entry in q:
            self.mysteps = entry.steps    

        return self.mysteps

    def gimmecurrlooks(self):
        looklist = []
        for l in Look.select():
            mystr = "<a href='%s'>%s</a>" %(l.link,l.look)
            looklist.append(mystr)
        self.looklist = looklist
        return self.looklist

    def gimmeclosestpoint(self):
        # mykeys = set().union(*(d.keys() for d in alistofdicts))
        # get the keys by querying the places
        mykeys = []
        q = Place.select()
        for entry in q:
            mykeys.append(int(entry.timestamp))

        mykey = min(mykeys, key=lambda x:abs(x - gimmecurseconds() ))

        q = Place.select().where(Place.timestamp == int(mykey))
        for entry in q:
            self.myplce = entry.point

        return self.myplce.y, self.myplce.x

    def gimmeclosestplace(self):
        # mykeys = set().union(*(d.keys() for d in alistofdicts))
        # get the keys by querying the places
        mykeys = []
        q = Place.select()
        for entry in q:
            mykeys.append(int(entry.timestamp))

        mykey = min(mykeys, key=lambda x:abs(x - gimmecurseconds() ))

        q = Place.select().where(Place.timestamp == int(mykey))
        for entry in q:
            self.myplce = entry.point

        return self.myplce



class Conversation(BaseModel):
    # record conversations with users
    actor = ForeignKeyField(Person, backref='conversations')
    message = TextField()
    timestamp = DateTimeField(default=datetime.now)


class Heart(BaseModel):
    actor = ForeignKeyField(Person, backref='heartbeats')
    timestamp = IntegerField()
    bpm = IntegerField()

    
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
