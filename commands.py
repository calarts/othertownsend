import logging
# Enable logging
logging.FileHandler('logs/tickererror.log')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# # # # # # # # # # # # # # # # # # # # # # # # # # 
# Define the command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
# from commands import start, pulse, feeling, sleep, loc, alarm, set_timer, unset, shutdown, stop
# # # # # # # # # # # # # # # # # # # # # # # # # # 

def start(update, context):
    mymsg = """Hi, I am the Other Townsend! Ask me questions like 
                "How are you feeling?",
                "How did you sleep?", 
                "Where are you?" and 
                "What are you looking at?" 
                You may also type /set <seconds> to get regular updates from me."""
    update.message.reply_text(mymsg)
    
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

