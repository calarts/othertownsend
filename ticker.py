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
import datetime
import json

from telegram.ext import Updater, CommandHandler

from _config import TOKEN

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

heartrate_file = "data/heart_rate-2019-01-06.json"
pulserecord = {}

with open(heartrate_file) as json_file:  
    data = json.load(json_file)
    for p in data:
        do = datetime.datetime.strptime(p['dateTime'], '%m/%d/%y %H:%M:%S')
        myseconds = (do.hour*3600)+(do.minute*60)+(do.second)
        pulserecord[myseconds]=str(p['value']['bpm'])

sortedpulse = dict(sorted(pulserecord.items()))


# get the pulse
def getpulsenow():
    rightnow = datetime.datetime.now()
    midnight = datetime.datetime.combine(rightnow.date(), datetime.time())
    mysecs = (rightnow - midnight).seconds
 
    # lookup the heartrate at this time:
    # min(myList, key=lambda x:abs(x-mysecs))
    mypulse = sortedpulse[mysecs] if mysecs in sortedpulse else sortedpulse[min(sortedpulse.keys(), key=lambda k: abs(k-mysecs))]
    timestr = datetime.datetime.now().strftime("%H:%M:%S")
    return mypulse, timestr

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')
    
def pulse(update):
    """Gimme your current heart-rate"""
    mypulse, timestr = getpulsenow()
    msg = "♥ " + str(mypulse) + " BPM ("+timestr+")️"
    update.message.reply_text(msg)

def loc():
    """Gimme your current location STUB"""
    msg = "lat = xxx, lon = yyy️"
    update.message.reply_text(msg)

def alarm(context):
    """Send the alarm message."""
    job = context.job
    mypulse, timestr = getpulsenow()
    msg = "♥ " + str(mypulse) + " BPM ("+timestr+") 💜 😴〰️"
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
	dp.add_handler(CommandHandler('stop', stop,
	                              pass_args=True,
	                              pass_job_queue=True,
	                              pass_chat_data=True))
	dp.add_handler(CommandHandler('pulse', pulse, pass_chat_data=True))
	dp.add_handler(CommandHandler('loc', loc))


	# Start the Bot
	updater.start_polling()

	# Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
	# SIGABRT. This should be used most of the time, since start_polling() is
	# non-blocking and will stop the bot gracefully.
	updater.idle()

if __name__ == '__main__':
    main()


