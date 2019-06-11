from datetime import datetime

from shapely.geometry import Point
from shapely.wkt import dumps, loads
from peewee import *
from flask import Flask, Blueprint
from flask_restplus import Resource, Api

from vars import Person, Heart, Brain, Place, Step, Look
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
blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, doc='/api')
app.register_blueprint(blueprint)


@api.route('/heartrate')
class HeartRate(Resource):
    def get(self):
        timestr = datetime.now().strftime("%H:%M:%S")
        mypulse = gimmebeats(heartrate_keylist)
        return {'heartrate': mypulse, 'timestr': timestr}

@api.route('/location')
class CurrentLocation(Resource):
    def get(self):
        timestr = datetime.now().strftime("%H:%M:%S")
        mykey, myplace = gimmeclosestplace()
        return {'myplace': myplace, 'mykey': mykey, 'timestr': timestr}

@api.route('/feelings')
class CurrentFeelings(Resource):
    def get(self):
        timestr = datetime.now().strftime("%H:%M:%S")
        return {'feelings': str(gimmeFeelings()[0]), 'timestr': timestr}

@api.route('/sleep')
class SleepQuality(Resource):
    def get(self):
        timestr = datetime.now().strftime("%H:%M:%S")
        return {'sleep': str(gimmeFeelings()[1]), 'timestr': timestr}


if __name__ == '__main__':
    app.run(debug=True)
