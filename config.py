import pygsheets
import string
from datetime import datetime, timedelta
from random import randint

# BOT IMPORTS----------------------------------------------------------------------
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

import schedule
import threading

# ----------------------------------------------------------------------
TOKEN = ''
CHAT_ID = ''
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
TEXT_ERROR = 'Кажется, сегодня воскресенье, пора обновить расписание'
# ----------------------------------------------------------------------
SHEET_INFO = ''
SHEET_WEEK = ''
# ----------------------------------------------------------------------
SHEET_MONEY = ''
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
def get_sheet_id_with_star(sheet):
    c = pygsheets.authorize(service_file='client_secret.json')
    sh = c.open_by_url(sheet)

    # Get sheet id with name with *****
    wks_list = sh.worksheets()[:5]
    wks_list = [x.jsonSheet['properties']['title'] for x in wks_list]
    sheet_id = [wks_list.index(x) for x in wks_list if '*' in x][0]

    return sheet_id
# ----------------------------------------------------------------------
