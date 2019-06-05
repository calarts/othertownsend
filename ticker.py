#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import threading
from datetime import datetime, date, timedelta, time
import simplejson as json
import csv, sys, os

from shapely.geometry import Point
from shapely.wkt import dumps, loads
from peewee import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext import BaseFilter

from geojson import LineString, Feature, Point, FeatureCollection
# import geojsonio

from vars import pulses, trips, times
from vars import Person, Heart, Brain, Place, Step
from vars import heartratedata, sleepdata, timepointdata, stepdata
from utils import gimmeFeelings, gimmeLongLat, gimmeGeojson
from utils import gimmeSeconds, gimmecurseconds, gimmeclosestkv
from utils import gimmecurrsteps, gimmeclosestplace, gimmebeats
from utils import createPersondb, createHeartdb, createPlacedb, createStepdb

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
# Define the command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
# # # # # # # # # # # # # # # # # # # # # # # # # # 

def start(update, context):
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')
    
def pulse(update, context):
    """Gimme your current heart-rate"""
    mypulse = gimmebeats(heartrate_keylist)
    msg = "♥ " + str(mypulse) + " BPM ("+timestr+")️"
    update.message.reply_text(msg)

def feeling(update, context):
    """Gimme your current mood"""
    mypulse = gimmebeats(heartrate_keylist)
    msg = str(gimmeFeelings()[0]) + " ("+timestr+")️"
    update.message.reply_text(msg)

def sleep(update, context):
    """Gimme your current heart-rate"""
    mypulse = gimmebeats(heartrate_keylist)
    msg = str(gimmeFeelings()[1]) + " ("+timestr+")️"
    update.message.reply_text(msg)

def loc(update, context):
    """Gimme your current location STUB"""
    # hacky! -- get the first position on our trip
    # you need to get the position in the duration
    msg = gimmeclosestplace()
    update.message.reply_text(msg)

def alarm(context):
    """Send the alarm message."""
    job = context.job
    mypulse = gimmebeats(heartrate_keylist)
    msg = str(gimmeFeelings()[0]) + str(gimmeFeelings()[1]) + str(gimmeclosestplace()) + str(mypulse) + " BPM ("+ str(timestr) +")"
    context.bot.send_message(job.context, text=msg)


def set_timer(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue
        # job = context.job_queue.run_once(alarm, due, context=chat_id)
        job = context.job_queue.run_repeating(alarm, due, context=chat_id)
        
        context.chat_data['job'] = job

        update.message.reply_text('👍')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update, context):
    """Remove the job if the user changed their mind."""
    if 'job' not in context.chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text('Timer successfully unset!')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    # context.bot.send_message(context, text='Update "%s" caused error "%s"', update, context.error)
    
def shutdown():
    # context.bot.send_message(job.context, text='Stopping...')
    updater.stop()
    updater.is_idle = False
    
def stop(update, context):
    threading.Thread(target=shutdown).start()


def reply_withfeeling(update, context):
    """How do you feel?"""
    mypulse = gimmebeats(heartrate_keylist)

    msg = "I feel " + str(gimmeFeelings()[0]) + str(mypulse) + " BPM"
    update.message.reply_text(msg)

def reply_withsleep(update, context):
    """How do you feel?"""
    msg = str(gimmeFeelings()[1])
    update.message.reply_text(msg)



def main():
    # """Run bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # Let's listen for specific questions:
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

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

    # listening for "feelins" and "sleep"
    dp.add_handler(feel_handler)
    dp.add_handler(sleep_handler)

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


