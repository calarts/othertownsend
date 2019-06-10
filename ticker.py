#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
This Bot uses the Updater class to handle the bot 
and the JobQueue to send timed messages.

First, a few handler functions are defined. 
Then, those functions are passed to the Dispatcher 
and registered at their respective places.
Then, the bot is started and runs 
until we press Ctrl-C on the command line.

Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal 
to the process to stop the bot.
"""

import logging
import threading
from datetime import datetime, date, timedelta, time
import simplejson as json
import csv, sys, os
from random import choice

from shapely.geometry import Point
from shapely.wkt import dumps, loads
from peewee import *
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import BaseFilter, Filters

from geojson import LineString, Feature, Point, FeatureCollection
# import geojsonio

from vars import pulses, trips, times
from vars import Person, Heart, Brain, Place, Step, Look
from vars import heartratedata, sleepdata, timepointdata, stepdata
from utils import gimmeFeelings, gimmeLongLat, gimmeGeojson
from utils import gimmeSeconds, gimmecurseconds, gimmeclosestkv
from utils import gimmecurrsteps, gimmeclosestplace, gimmebeats
from utils import createPersondb, createHeartdb, gimmecurrlooks
from utils import createPlacedb, createStepdb, createLookdb
from commands import error, start, pulse, feeling, sleep, loc
from commands import alarm, set_timer, unset, shutdown, stop

from _config import TOKEN, DEBUG

# Enable logging
logging.FileHandler('logs/tickererror.log')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

timestr = datetime.now().strftime("%H:%M:%S")

if DEBUG:
    mydb = SqliteDatabase(':memory:')
else:
    mydb = SqliteDatabase("other.db")


# # # # # # # # # # # # # # # # # # # # # # # # # # 
# create the tables and populate them if necessary
# # # # # # # # # # # # # # # # # # # # # # # # # # 

other = createPersondb(mydb)
createHeartdb(mydb,other)
createStepdb(mydb,other)
createPlacedb(mydb,other)
createLookdb(mydb,other)

# You don't want to run these on every query!
heartrate_keylist = []
q = Heart.select(Heart.timestamp)
for t in q:
    heartrate_keylist.append( int(t.timestamp) )

# You don't want to run this on every query
step_keylist = []
q = Step.select(Step.timestamp)
for t in q:
    step_keylist.append( int(t.timestamp) )


# # # # # # # # # # # # # # # # # # # # # # # # # # 
# conversations
# 
# # # # # # # # # # # # # # # # # # # # # # # # # # 

def reply_withfeeling(update, context):
    """How do you feel?"""
    mypulse = gimmebeats(heartrate_keylist)
    mood = gimmeFeelings()[2]
    if mood == 1:
        replies = ["Thanks for asking! I feel great. ",
                "I'm doing pretty well today, thanks! ",
                "Good, see for yourself. ",
                "What could go wrong with stats like these? ",
                "Never better! ",
                "See for yourself! ",
                "Great! ",
                "Check me out! ",
                "Good, thanks. "
                ""]
    else:
        replies = ["Good! Why do you ask? ",
                "What do you think? ",
                "Maybe you can tell me? ",
                "Why do you want to know? ",
                "Who's asking? ",
                "ok, thanks. ",
                "Does it matter? ",
                "Why would I want to tell you? ",
                "Been better ",
                "Does it matter? "
                ""]

    msg = choice(replies) + str(gimmeFeelings()[0]) + str(mypulse) + " BPM"
    update.message.reply_text(msg)

def reply_withsleep(update, context):
    """How did you sleep?"""
    msg = str(gimmeFeelings()[1])
    update.message.reply_text(msg)

def reply_withphoto(update,context):
    """Where are you? Send a photo of a place."""
    imgs = ["media/37.64961_-122.45323.jpg",
            "media/37.7919_-122.4038.jpg",
            "media/37.914996_-122.533479.jpg"
            "media/37.74006_-121.95199.jpg",
            "media/37.880985_-122.526087.jpg",
            "media/37.927329_-122.580594.jpg"
            "media/37.77838_-122.389240.jpg",
            "media/37.905995_-122.554277.jpg"]

    update.message.reply_photo(photo=open(choice(imgs), 'rb'))


def reply_withhtml(update,context):
    """What are you looking at?"""
    looklist = gimmecurrlooks()
    lk = choice(looklist)
    update.message.reply_html( str(lk) )

 
def main():
    # """Run bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # Let's listen for specific questions:
    # ADD LOOKS!
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    
    # What are you looking at??
    class FilterLook(BaseFilter):
        def filter(self, message):
            return 'looking at?' in message.text

    filter_look = FilterLook()
    
    look_handler = MessageHandler(filter_look, reply_withhtml)
    


    # Where are you?
    class FilterWhere(BaseFilter):
        def filter(self, message):
            return 'Where are you?' in message.text

    # Where are you?
    class FilterWheresimple(BaseFilter):
        def filter(self, message):
            return 'where' in message.text

    filter_where = FilterWhere()
    filter_wheresimple = FilterWheresimple()

    where_handler = MessageHandler(filter_where | filter_wheresimple, reply_withphoto)
    
    
    # Many questions about feelings, same response
    # How are you feeling/How do you feel/How has your day been? (Mood, BPM)

    class FilterFeel(BaseFilter):
        def filter(self, message):
            return 'you feel?' in message.text

    class FilterFeeling(BaseFilter):
        def filter(self, message):
            return 'you feeling?' in message.text

    class DayBeen(BaseFilter):
        def filter(self, message):
            return 'day been?' in message.text

    filter_feel = FilterFeel()
    filter_feeling = FilterFeeling()
    day_been = DayBeen()
    feel_handler = MessageHandler(filter_feel | filter_feeling | day_been, reply_withfeeling)
    

    # One question about sleep, same response
    # How did you sleep? (sleep)
    class FilterSleep(BaseFilter):
        def filter(self, message):
            return 'you sleep?' in message.text

    filter_sleep = FilterSleep()
    sleep_handler = MessageHandler(filter_sleep, reply_withsleep)


    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # listening for "feelings" and "sleep"
    dp.add_handler(feel_handler)
    dp.add_handler(sleep_handler)
    dp.add_handler(where_handler)
    dp.add_handler(look_handler)

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)
    # add a stop handler
    dp.add_handler(CommandHandler('stop', stop))
    dp.add_handler(CommandHandler('pulse', pulse, pass_chat_data=True))
    dp.add_handler(CommandHandler('loc', loc, pass_chat_data=True))
    dp.add_handler(CommandHandler('feeling', feeling, pass_chat_data=True))
    dp.add_handler(CommandHandler('sleep', sleep, pass_chat_data=True))


    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()


