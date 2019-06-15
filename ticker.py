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

from models import Person, Heart, Step, Conversation
from vars import heartratedata, sleepdata, timepointdata, stepdata
# from utils import gimmeLongLat, gimmeGeojson
# from utils import gimmeSeconds, gimmecurseconds
from utils import createPersondb, createHeartdb
from utils import createPlacedb, createStepdb, createLookdb, createConversationdb
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

createConversationdb(mydb)

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

# Here's what's in a MESSAGE
# {
#     'message_id': 2497,
#     'date': 1560323509,
#     'chat': {
#         'id': 730104154,
#         'type': 'private',
#         'username': 'dgoodwin',
#         'first_name': 'Douglas',
#         'last_name': 'Goodwin'
#     },
#     'text': 'are you recording this?',
#     'entities': [],
#     'caption_entities': [],
#     'photo': [],
#     'new_chat_members': [],
#     'new_chat_photo': [],
#     'delete_chat_photo': False,
#     'group_chat_created': False,
#     'supergroup_chat_created': False,
#     'channel_chat_created': False,
#     'from': {
#         'id': 730104154,
#         'first_name': 'Douglas',
#         'is_bot': False,
#         'last_name': 'Goodwin',
#         'username': 'dgoodwin',
#         'language_code': 'en'
#     }
# }

# {
# 	'message_id': 2570,
# 	'date': 1560385165,
# 	'chat': {
# 		'id': 730104154,
# 		'type': 'private',
# 		'username': 'dgoodwin',
# 		'first_name': 'Douglas',
# 		'last_name': 'Goodwin'
# 	},
# 	'text': 'how are you feeling?',
# 	'entities': [],
# 	'caption_entities': [],
# 	'photo': [],
# 	'new_chat_members': [],
# 	'new_chat_photo': [],
# 	'delete_chat_photo': False,
# 	'group_chat_created': False,
# 	'supergroup_chat_created': False,
# 	'channel_chat_created': False,
# 	'from': {
# 		'id': 730104154,
# 		'first_name': 'Douglas',
# 		'is_bot': False,
# 		'last_name': 'Goodwin',
# 		'username': 'dgoodwin',
# 		'language_code': 'en'
# 	}
# }


def reply_withgreeting(update, context):
    """reply with simple hallos"""
    feelings = other.get_mymood()   # this sets mood
    if other.mood == 1:
        replies = ["hi",
                "hey,",
                "what's up",
                "yo",
                "how you been",
                "👋",
                "🤝",
                "🖐️",
                "🖖"]
    else:
        replies = ["👋",
                "👾",
                "yo",
                "🖐️",
                "k",
                "howdy"]
    if update.message.from_user.first_name:
        personalreply = str(update.message.from_user.first_name)
    else:
        personalreply = str(update.message.from_user.name)
    msg = choice(replies) +" "+ personalreply
    update.message.reply_text(msg)


def reply_withfeeling(update, context):
    """How do you feel?"""
    mypulse = other.gimmebeats(heartrate_keylist)
    feelings = other.get_mymood()   # this sets mood
    if other.mood == 1:
        replies = ["Thanks for asking! I feel great. ",
                "I'm doing pretty well today, thanks! ",
                "Good, see for yourself. ",
                "What could go wrong with numbers like these? ",
                "Never better! ",
                "See for yourself! ",
                "Great! ",
                "Check me owwt! ",
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
    # if update.message.from_user.first_name:
    #     personalreply = "Hey " + str(update.message.from_user.first_name) + "!\n"
    # else:
    #     personalreply = "Hi " + str(update.message.from_user.name) + ".\n"
    msg = choice(replies) + str(other.get_mymood()) + str(mypulse) + " BPM"
    update.message.reply_text(msg)

def reply_withsleep(update, context):
    """How did you sleep?"""
    reply = other.get_personalreply(update,themeat=str(other.get_mysleep()))
    update.message.reply_text(reply)

def reply_withphoto(update,context):
    """Where are you? Send a photo of a place."""
    reply = other.get_personalreply(update,themeat=str(other.get_mymood()))
    imgs = ["media/37.64961_-122.45323.jpg",
            "media/37.7919_-122.4038.jpg",
            "media/37.914996_-122.533479.jpg"
            "media/37.74006_-121.95199.jpg",
            "media/37.880985_-122.526087.jpg",
            "media/37.927329_-122.580594.jpg",
            "media/37.77838_-122.389240.jpg",
            "media/37.905995_-122.554277.jpg"]

    update.message.reply_photo(photo=open(choice(imgs), 'rb'))


def reply_withhtml(update,context):
    """What are you looking at?"""
    looklist = other.gimmecurrlooks()
    lk = choice(looklist)
    update.message.reply_html( str(lk) )

def recordconvo(message):
    """Record contact from humans and others"""
    fn = message.from_user.first_name
    ln = message.from_user.last_name
    lg = message.from_user.username
    lc = message.from_user.language_code
    ti = message.from_user.id
    cn = message.from_user.name
    msg = message.text
    
    try:
        chatee = Person.get(Person.telegram_id == ti)
    except Person.DoesNotExist:
        chatee = Person.create(
            name=lg,
            login=lg,
            chat_name=cn,
            telegram_id=ti,
            created_at=datetime.now(),
            first_name=fn,
            last_name=ln,
            language_code=lc 
            )
        try:
            chatee.save()
        except:
            print("couldn't save this Chatee!",fn,ln,ti)

    convo = Conversation.create(
        actor=chatee, 
        message=msg
        )
    try:
        convo.save()
    except:
        print("couldn't save this Conversation!",chatee,msg)

 
def main():
    # """Run bot."""

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # Let's listen for specific questions:
    # ADD LOGGING to display on the Feather!
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    # simple greetings
    class FilterGreetings(BaseFilter):
        def filter(self, message):
            amitrue = ('hi' in message.text or 'hey' in message.text or 'hello' in message.text)
            return amitrue

    filter_greetings = FilterGreetings()
    greetings_handler = MessageHandler(filter_greetings, reply_withgreeting)


    # What are you looking at??
    class FilterLook(BaseFilter):
        def filter(self, message):
            amitrue = ('looking' in message.text or 'look' in message.text)
            # this little hack will record all text messages
            if amitrue:
                recordconvo(message)
            else:
                recordconvo(message)
            return amitrue

    filter_look = FilterLook()
    look_handler = MessageHandler(filter_look, reply_withhtml)
    

    # Where are you?
    class FilterWhere(BaseFilter):
        def filter(self, message):
            amitrue = ('where' in message.text or 'Where' in message.text)
            return amitrue

    filter_where = FilterWhere()
    where_handler = MessageHandler(filter_where, reply_withphoto)
    
    
    # Many questions about feelings, same response
    # How are you feeling/How do you feel/How has your day been? (Mood, BPM)

    class FilterFeel(BaseFilter):
        def filter(self, message):
            amitrue = ('feel' in message.text or 'feeling' in message.text or 'been?' in message.text)
            return amitrue

    filter_feel = FilterFeel()
    feel_handler = MessageHandler(filter_feel, reply_withfeeling)
    

    # One question about sleep, same response
    # How did you sleep? (sleep)
    class FilterSleep(BaseFilter):
        def filter(self, message):
            amitrue = ('sleep' in message.text)
            return amitrue

    filter_sleep = FilterSleep()
    sleep_handler = MessageHandler(filter_sleep, reply_withsleep)


    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # listening for "feelings" and "sleep"
    dp.add_handler(greetings_handler)
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


