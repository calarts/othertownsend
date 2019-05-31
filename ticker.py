#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# If you're still using version 11.1.0, please see the examples at
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

"""
Simple Bot to send timed Telegram messages.

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
import json

from telegram.ext import Updater, CommandHandler
# from geojson import LineString, MultiLineString, Feature, Point, FeatureCollection
# import geojsonio

from vars import pulses, trips, times


from _config import TOKEN

# Enable logging
logging.FileHandler('logs/tickererror.log')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

heartrate_file = "data/heart_rate-2019-01-06.json"
pulserecord = {}

with open(heartrate_file) as json_file:  
    data = json.load(json_file)
    for p in data:
        do = datetime.strptime(p['dateTime'], '%m/%d/%y %H:%M:%S')
        myseconds = (do.hour*3600)+(do.minute*60)+(do.second)
        pulserecord[myseconds]=str(p['value']['bpm'])

sortedpulse = dict(sorted(pulserecord.items()))


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end
    
def gimmeTimedelta(s):
    return timedelta(hours=s.hour, minutes=s.minute, seconds=s.second).total_seconds()

def gimmeLongLat(stups):
    # ugh, must reverse lat and lng
    revtups = []
    for tup in stups:
        revtups.append(tup[::-1])
    return revtups

# def gimmeGeojson(atrip):
#     # ugh, must reverse lat and lng
#     revtups = gimmeLongLat(atrip)
#     myline = LineString(revtups)
#     myfeature = Feature(geometry=myline)
#     myfeaturecollection = FeatureCollection(myfeature)
#     return myfeaturecollection

def get_curtimeslot(timeslots):
    curtime = datetime.now().time()
#     curtime = (datetime.time(15, 7, 6, 952394))
    for idx,slot in enumerate(timeslots):
        if time_in_range(slot['start'], slot['end'], curtime):
#             print('got one!',idx,slot)
            myslot = idx
            t1 = gimmeTimedelta(slot['start'])
            t2 = gimmeTimedelta(slot['end'])
            ct = gimmeTimedelta(curtime)
            duration = (t2-t1)
            timeintotrip = (ct-t1)
            # myfeaturecollection = gimmeGeojson(trips[myslot])
    return(curtime,myslot,duration,timeintotrip,trips[myslot])

curtime,myslot,duration,timeintotrip,trips[myslot] = get_curtimeslot(times)

# get the pulse
def getpulsenow():
    rightnow = datetime.now()
    midnight = datetime.combine(rightnow.date(), time())
    mysecs = (rightnow - midnight).seconds
 
    # lookup the heartrate at this time:
    # min(myList, key=lambda x:abs(x-mysecs))
    mypulse = sortedpulse[mysecs] if mysecs in sortedpulse else sortedpulse[min(sortedpulse.keys(), key=lambda k: abs(k-mysecs))]
    timestr = datetime.now().strftime("%H:%M:%S")
    return mypulse, timestr

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')
    
def pulse(update, context):
    """Gimme your current heart-rate"""
    mypulse, timestr = getpulsenow()
    msg = "♥ " + str(mypulse) + " BPM ("+timestr+")️"
    update.message.reply_text(msg)

def feeling(update, context):
    """Gimme your current mood"""
    mypulse, timestr = getpulsenow()
    feelings = ["💜","💜","💜","💜","💜","💜","💜","💛","💛","💛","💛","💛","💜","💜","💜","💜","💜","💛",]
    msg = str(feelings[myslot]) + " ("+timestr+")️"
    update.message.reply_text(msg)

def sleep(update, context):
    """Gimme your current heart-rate"""
    mypulse, timestr = getpulsenow()
    sleeps = ["➖","➖","➖","➖","➖","〰️","〰️","〰️","〰️","〰️","〰️","〰️","➖","➖","➖","➖","➖","〰️",]
    msg = str(sleeps[myslot]) + " ("+timestr+")️"
    update.message.reply_text(msg)

def loc(update, context):
    """Gimme your current location STUB"""
    # hacky! -- get the first position on our trip
    # you need to get the position in the duration
    msg = trips[myslot][0]
    update.message.reply_text(msg)

def alarm(context):
    """Send the alarm message."""
    job = context.job
    mypulse, timestr = getpulsenow()
    feelings = ["💜","💜","💜","💜","💜","💜","💜","💛","💛","💛","💛","💛","💜","💜","💜","💜","💜","💛",]
    sleeps = ["➖","➖","➖","➖","➖","〰️","〰️","〰️","〰️","〰️","〰️","〰️","➖","➖","➖","➖","➖","〰️",]
    msg = str(sleeps[myslot]) + str(sleeps[myslot]) + str(trips[myslot][0]) + str(mypulse) + " BPM ("+ str(timestr) +")"
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

def main():
    # """Run bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

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


