#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

import time
import datetime

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, PhotoSize)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)


# get Authentication token
with open("config.txt", "r") as f:
    AUTH_TOKEN = f.readline()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

STUDY = 1
ASK_STUDY = 2
BREAK = 3
ASK_BREAK = 4

POMODORO_IMG = PhotoSize("https://www.silhcdn.com/3/i/shapes/lg/0/4/d81740.jpg",  width=2, height=10, file_size=2, file_unique_id=0)
BREAK_IMG = PhotoSize("https://i.pinimg.com/originals/f6/62/27/f66227b47155e5996ac37cca75e81de3.jpg", width=2, height=2, file_unique_id=1)
# Study-time and break-time in minutes:
STUDY_TIME_SHORT = 25
STUDY_TIME_LONG = 50

BREAK_TIME_SHORT = 5
BREAK_TIME_LONG = 10

SHOW_TIME_INTERVAL = 10


def start(update, context):
    reply_keyboard = [['{} min'.format(STUDY_TIME_SHORT), '{} min'.format(STUDY_TIME_LONG)]]

    update.message.reply_text(
        'Hi! My name is Pomodoro Bot. I will start a Pomodoro-timer for you. '
        'Send /cancel when you are too lazy to study...\n\n'
        'How long do you want your first Pomodoro to be?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return STUDY


def display_countdown(bot, chat_id, seconds):
    start = datetime.datetime.now()
    sent_msg = bot.send_message(
        chat_id=chat_id,
        text='Time left: <b>{0:02d}:{1:02d}</b>.'.format(seconds//60, seconds%60),
        parse_mode='HTML'
        )

    while (datetime.datetime.now()-start).seconds < seconds:
    #for sec in range(SHOW_TIME_INTERVAL, seconds+1, SHOW_TIME_INTERVAL):
        seconds_left = max(0,seconds-(datetime.datetime.now()-start).seconds)
        try:
            bot.edit_message_text(
                chat_id=sent_msg.chat_id,
                message_id=sent_msg.message_id,
                text='Time left: <b>{0:02d}:{1:02d}</b>.'.format(seconds_left//60, seconds_left%60),
                parse_mode='HTML'
                )
        except:
            pass
        time.sleep(SHOW_TIME_INTERVAL)

def study_time(update, context):
    now = datetime.datetime.now()
    duration = int(update.message.text.split(' ')[0])
    current_message = update.message.reply_text('--==   <b>Pomodoro</b>   ==--\nDuration:\t{0} min\nStart:\t{1:02d}:{2:02d}!'.format(duration, now.hour, now.minute),
                                reply_markup=ReplyKeyboardRemove(),
                                parse_mode='HTML')

    bot = current_message.bot

    bot.send_photo(chat_id=current_message.chat_id, photo=POMODORO_IMG)

    display_countdown(bot, current_message.chat_id, duration*60)

    reply_keyboard = [['{} min'.format(BREAK_TIME_SHORT), '{} min'.format(BREAK_TIME_LONG)]]

    update.message.reply_text(
        'Now you deserve a break!\nHow long do you want to have a break?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return BREAK


def break_time(update, context):
    now = datetime.datetime.now()
    duration = int(update.message.text.split(' ')[0])
    current_message = update.message.reply_text('--==    <b>Break</b>    ==--\nDuration:\t{0} min\nStart:\t{1:02d}:{2:02d}!'.format(duration, now.hour, now.minute),
                                reply_markup=ReplyKeyboardRemove(),
                                parse_mode='HTML')

    bot = current_message.bot

    bot.send_photo(chat_id=current_message.chat_id, photo=BREAK_IMG)


    display_countdown(bot, current_message.chat_id, duration*60)

    reply_keyboard = [['{} min'.format(STUDY_TIME_SHORT), '{} min'.format(STUDY_TIME_LONG)]]

    update.message.reply_text(
        'It\'s time to study!\nChoose a time for your next Pomodoro!',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return STUDY


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope you will continue studying again soon!',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    print("         >>>   Starting Pomodoro Bot   <<<")

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(AUTH_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            STUDY: [MessageHandler(Filters.text, study_time)],

            BREAK: [MessageHandler(Filters.text, break_time)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()