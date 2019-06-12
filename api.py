from datetime import datetime

from shapely.geometry import Point
from shapely.wkt import dumps, loads
from peewee import *
from flask import Flask, Blueprint
from flask_restplus import Resource, Api

from vars import Person, Heart, Brain, Place, Step, Look, Conversation
from utils import gimmeLongLat, gimmeGeojson, gimmeSeconds, gimmeFeelings
from utils import gimmecurseconds, gimmeclosestkv, gimmecurrsteps
from utils import gimmeclosestplace, gimmecurrlooks, gimmebeats

heartrate_keylist = []
q = Heart.select(Heart.timestamp)
for t in q:
    heartrate_keylist.append( int(t.timestamp) )

# You don't want to run this on every query
step_keylist = []
q = Step.select(Step.timestamp)
for t in q:
    step_keylist.append( int(t.timestamp) )

mood = gimmeFeelings()[2]

app = Flask(__name__)
# set the base URL with a blueprint
blueprint = Blueprint('devapi', __name__, url_prefix='/devapi')
devapi = Api(blueprint)
app.register_blueprint(blueprint)


@devapi.route('/heartrate')
class HeartRate(Resource):
    def get(self):
        timestr = datetime.now().strftime("%H:%M:%S")
        mypulse = gimmebeats(heartrate_keylist)
        return {'heartrate': mypulse, 'timestr': timestr}

@devapi.route('/location')
class CurrentLocation(Resource):
    def get(self):
        timestr = datetime.now().strftime("%H:%M:%S")
        mykey, myplace = gimmeclosestplace()
        return {'myplace': myplace, 'mykey': mykey, 'timestr': timestr}

@devapi.route('/feelings')
class CurrentFeelings(Resource):
    def get(self):
        timestr = datetime.now().strftime("%H:%M:%S")
        return {'feelings': str(gimmeFeelings()[0]), 'timestr': timestr}

@devapi.route('/sleep')
class SleepQuality(Resource):
    def get(self):
        timestr = datetime.now().strftime("%H:%M:%S")
        return {'sleep': str(gimmeFeelings()[1]), 'timestr': timestr}


@devapi.route('/conversations')
class MyConversations(Resource):
    def get(self):
        query = (Conversation
         .select(Conversation.first_name,Conversation.last_name,Conversation.timestamp,Conversation.message)
         .order_by(Conversation.timestamp.desc()))

    # first_name = CharField()
    # last_name = CharField()
    # login = CharField()
    # language_code = CharField()
    # telegram_id = CharField()
    # message = TextField()
    # timestamp = DateTimeField(default=datetime.now)

        myconvos = []
        for convo in query:
            myd = {'first_name': Conversation.first_name,'last_name': Conversation.last_name,'message': Conversation.message,,'timestamp': Conversation.timestamp}
            myconvos.append(myd)
            print(myd)

    return json.dumps(myconvos)


if __name__ == '__main__':
    app.run(debug=True)
