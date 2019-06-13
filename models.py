from datetime import time, datetime
from peewee import *

from _config import DEBUG

if DEBUG:
    mydb = SqliteDatabase(':memory:')
else:
    mydb = SqliteDatabase("other.db")

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

class Conversation(BaseModel):
    # record conversations with users
    actor = ForeignKeyField(Person, backref='conversations')
    message = TextField()
    timestamp = DateTimeField(default=datetime.now)


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
