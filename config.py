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
CHAT_ID = '887971750'
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
TEXT_ERROR = 'Кажется, сегодня воскресенье, пора поставить звездочку на новую страницу'
# ----------------------------------------------------------------------
SHEET_INFO = 'https://docs.google.com/spreadsheets/d/1ennBAXi3vGJmvk8nBkmTqEtwCeNlRhh7pt3axqAmK3s/edit?usp=sharing'
SHEET_WEEK = 'https://docs.google.com/spreadsheets/d/19UQgj7yZD2BEPuuyAN9Vt7XPoxMkiJND_STV-ojX-ok/edit#gid=736077533'
# ----------------------------------------------------------------------
SHEET_MONEY = 'https://docs.google.com/spreadsheets/d/1l29b_E6NR4R3GnW8s8C2aTVZGgRQo4_QF3RY0YMdta0/edit?usp=sharing'
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
