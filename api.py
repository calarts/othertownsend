from datetime import datetime

from shapely.geometry import Point
from shapely.wkt import dumps, loads
from peewee import *
from flask import Flask, Blueprint
from flask_restplus import Resource, Api

from models import Person, Heart, Place, Step, Look, Conversation
from utils import gimmeLongLat, gimmeGeojson, gimmeSeconds
from utils import gimmecurseconds

heartrate_keylist = []
q = Heart.select(Heart.timestamp)
for t in q:
    heartrate_keylist.append( int(t.timestamp) )

# You don't want to run this on every query
step_keylist = []
q = Step.select(Step.timestamp)
for t in q:
    step_keylist.append( int(t.timestamp) )

other = Person.get(name='OTHER')
mood = other.get_mymood()[1]

app = Flask(__name__)
# set the base URL with a blueprint
blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint)
app.register_blueprint(blueprint)


@api.route('/heartrate')
class HeartRate(Resource):
    def get(self):
        timestr = datetime.now().strftime("%H:%M:%S")
        mypulse = other.gimmebeats(heartrate_keylist)
        return {'heartrate': mypulse, 'timestr': timestr}

@api.route('/location')
class CurrentLocation(Resource):
    def get(self):
        timestr = datetime.now().strftime("%H:%M:%S")
        mykey, myplace = other.gimmeclosestplace()
        return {'myplace': myplace, 'mykey': mykey, 'timestr': timestr}

@api.route('/feelings')
class CurrentFeelings(Resource):
    def get(self):
        timestr = datetime.now().strftime("%H:%M:%S")
        return {'feelings': str(other.get_mymood()), 'timestr': timestr}

@api.route('/state')
class CurrentState(Resource):
    """an aggregate of feelings prepared for ArduinoJson"""
    def get(self):
        timestr = datetime.now().strftime("%s")            # we want a UNIX timestring
        mymood = "❤"                                       # this seems to be legal
        mysleep = "--"
        # but this one gives you 0 or 1
        if other.get_mymood()[1] == 1:
            mymood = "❤"
        else:
            mymood = "o"
        mylat,mylon= other.gimmeclosestpoint()
        return {'mymood': str(mymood),
        		'mood': other.get_mymood()[1],
        		'timestr': int(timestr), 
        		'sleep': str(other.get_mysleep()),
        		'heartrate': other.gimmebeats(heartrate_keylist),
        		'steps': other.gimmecurrsteps(step_keylist),
        		'location': [mylat,mylon]}

@api.route('/sleep')
class SleepQuality(Resource):
    def get(self):
        timestr = datetime.now().strftime("%H:%M:%S")
        return {'sleep': str(other.get_mysleep()), 'timestr': timestr}

@api.route('/conversations/-1')
class LatestConversation(Resource):
    def get(self):
        convo = Conversation.select().order_by(Conversation.timestamp.desc()).get()
        myd = {'first_name': str(convo.actor.first_name),
                    'last_name': str(convo.actor.last_name),
                    'message': str(convo.message),
                    'timestamp': str(convo.timestamp)
                    }

        return myd


@api.route('/conversations')
class MyConversations(Resource):

    def get(self):
        myconvos = []
        query = (Conversation
                .select()
                .join(Person, on=(Conversation.actor == Person.id)))

        for convo in query:
            myd = {'first_name': str(convo.actor.first_name),
                    'last_name': str(convo.actor.last_name),
                    'message': str(convo.message),
                    'timestamp': str(convo.timestamp)
                    }
            print(myd)
            myconvos.append(myd)

        return myconvos


if __name__ == '__main__':
    app.run(debug=True)
