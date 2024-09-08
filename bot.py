from config import *
from notification import *
from money import *

bot = telebot.TeleBot(TOKEN)


def gen_help_markup():
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton("/money"))
    markup.add(KeyboardButton('/next_deal'))
    markup.add(KeyboardButton('/tomorow'), KeyboardButton('/today'))
    markup.add(KeyboardButton('/get_notification_for_tomorow'))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "У вас уже есть команда?", reply_markup=gen_help_markup())
    bot.send_message(message.chat.id, f"Бот активирован! 🤖")


@bot.message_handler(commands=['tomorow'])
def send_message(message):
    sheet_id = get_sheet_id_with_star(SHEET_WEEK)
    text = get_day_info(sheet_id)[0]
    bot.send_message(CHAT_ID, "Твои планы на завтра:\n\n"+text, parse_mode="Markdown")

@bot.message_handler(commands=['get_notification_for_tomorow'])
def send_message(message):
    sheet_id = get_sheet_id_with_star(SHEET_WEEK)
    text, list_mes = get_day_info(sheet_id)
    bot.send_message(CHAT_ID, "Твои планы на завтра:\n\n"+text, parse_mode="Markdown")
    if text != TEXT_ERROR:
        for mes in list_mes:
            bot.send_message(CHAT_ID, mes[0] )#, parse_mode="Markdown")
            bot.send_message(CHAT_ID, mes[1])


@bot.message_handler(commands=['today'])
def send_message(message):
    sheet_id = get_sheet_id_with_star(SHEET_WEEK)
    text = get_day_info(sheet_id, (datetime.today()+ timedelta(hours=3)).strftime('%d.%m.%Y'))[0]
    bot.send_message(CHAT_ID, "Твои планы на сегодня:\n\n"+text, parse_mode="Markdown")


def money_0():
    global result_dict, str_id, sheet_id
    sheet_id = get_sheet_id_with_star(SHEET_MONEY)
    categories_list, subcategories_list  = get_data_by_column_from_money_sheet(sheet_id, ['1:2'])[0]
    result_dict = create_dict_with_data(categories_list, subcategories_list)

    today = str(int((datetime.today()+timedelta(hours=3)).strftime('%d')))
    str_id = get_id_of_date(sheet_id, today)
    return result_dict, str_id

@bot.message_handler(commands=['money'])
def money_1(message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton('Получила прибыль', callback_data='income'),
                   InlineKeyboardButton("Потратила деньги", callback_data='expense'),
                   InlineKeyboardButton("ОТМЕНА 🚫", callback_data='error'))
    bot.send_message(CHAT_ID, 'Выберите:', reply_markup=markup)


def gen_markup_cat(list):
    markup = InlineKeyboardMarkup(row_width=1)
    for el in list:
        markup.add(InlineKeyboardButton(el, callback_data=f'cat_{el}'))
    markup.add(InlineKeyboardButton("НАЗАД 🚫", callback_data=f'cat_НАЗАД'))
    return markup

def gen_markup_subcat(list):
    markup = InlineKeyboardMarkup(row_width=1)
    for el in list:
        markup.add(InlineKeyboardButton(el, callback_data=f'subcat_{el}'))
    markup.add(InlineKeyboardButton("НАЗАД 🚫", callback_data=f'subcat_НАЗАД'))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global result_dict, str_id, i, input_1, input_3, money, sheet_id, subcats

    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    # bot.edit_message_text(chat_id = call.message.chat.id, message_id=call.message.message_id, text=f"Выбрано: {call.data} 👌")

    if call.data == 'income' or call.data == 'expense' or call.data == 'error':
        if call.data == 'error':
            bot.send_message(call.message.chat.id, "Выбирайте другую команду", reply_markup=gen_help_markup())
            return
        input_1 = call.data
        bot.send_message(CHAT_ID, 'Выберите:', reply_markup=gen_markup_cat(result_dict[call.data]['categories']))

    if call.data.startswith('cat_'):
        cat = call.data[4:]
        if cat == 'НАЗАД':
            money_1(call.message)
            return
        i = result_dict[input_1]['categories'].index(cat)
        subcats = result_dict[input_1]['subcategories'][i]
        if subcats[0]:
            bot.send_message(CHAT_ID, 'Выберите:', reply_markup=gen_markup_subcat(subcats))
        else:
            res_id_in_main_dict = result_dict[input_1]['indexes'][i]
            money_2(call.message, res_id_in_main_dict)

    if call.data.startswith('subcat_'):
        input_3 = call.data[7:]
        if input_3 == 'НАЗАД':
            bot.send_message(CHAT_ID, 'Выберите:', reply_markup=gen_markup_cat(result_dict[input_1]['categories']))
            return
        res_id_in_main_dict = result_dict[input_1]['subindexes'][i][subcats.index(input_3)]
        money_2(call.message, res_id_in_main_dict)


def money_2(message, res_id_in_main_dict):

    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(KeyboardButton("ОТМЕНА 🚫"))

    bot.send_message(CHAT_ID, 'Сколько:', reply_markup = markup)
    bot.register_next_step_handler(message, money_3, res_id_in_main_dict=res_id_in_main_dict )

def money_3(message, res_id_in_main_dict):
    money = message.text
    if money.isdigit():
        money = int(money)
        money_4 (money = money, res_id_in_main_dict=res_id_in_main_dict)
        return
    elif money == 'ОТМЕНА 🚫':
        bot.send_message(CHAT_ID, 'оки, ничего не записалось', reply_markup=gen_help_markup())
    else:
        bot.send_message(CHAT_ID, 'Нужно ввести число!:')
        bot.register_next_step_handler(message, money_3, res_id_in_main_dict=res_id_in_main_dict)

def money_4(money, res_id_in_main_dict):
    addr = return_addr(str_id+1, res_id_in_main_dict)
    update_value_in_sheet(sheet_id, addr, money)
    bot.send_message(CHAT_ID, 'ГОТОВО ❇️', reply_markup=gen_help_markup())

@bot.message_handler(commands=['next_deal'])
def send_next_deal(message):
    text = get_next_deal()
    bot.send_message(CHAT_ID, text, reply_markup=gen_help_markup(), parse_mode="Markdown")

def send_notification(message):
    time = (datetime.now()+timedelta(minutes=5)+ timedelta(hours=3)).strftime("%H:%M")
    sheet_id = get_sheet_id_with_star(SHEET_WEEK)
    text = get_deal_for_time(time, sheet_id)
    if text:
        bot.send_message(CHAT_ID, text)
    else:
        try:
            bot.edit_message_text(text=f'{(datetime.now()+ timedelta(hours=3)).strftime("%H:%M")}', chat_id=message.chat.id, message_id = 478)
        except:
            print("oh")
    #     bot.send_message(CHAT_ID, 'Ближайшие полчаса дел нет')

def shedule_thread():
    schedule.every().day.at("19:14").do(send_message, message = '')
    schedule.every().day.at("00:01").do(money_0)
    schedule.every().hours.at(":55").do(send_notification, message = '')
    schedule.every().hours.at(":25").do(send_notification, message = '')
    # schedule.every().day.at("10:00").do(send_notification, message = '') # список дел!!!!! и напоминание каждый час про урок
    while True:
        schedule.run_pending()
        time.sleep(1)

def polling_thread_def():
    try:
        bot.polling(none_stop=True, timeout=120)
    except ReadTimeout as e:
        # Обработка ошибки ReadTimeout
        bot.send_message(message.chat.id, "Извините, возникла ошибка. Попробуйте позже.")
        bot.polling(none_stop=True, timeout=120)


if __name__ == '__main__':
    money_0()

    polling_thread = threading.Thread(target=polling_thread_def)
    polling_shedule  = threading.Thread(target=shedule_thread)

    polling_thread.start()
    polling_shedule.start()
