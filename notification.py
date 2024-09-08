import pygsheets
from collections import defaultdict
from datetime import datetime, timedelta
from random import randint


text_error = 'Кажется, сегодня воскресенье, пора поставить звездочку на новую страницу'
# ----------------------------------------------------------------------
sheet_info = 'https://docs.google.com/spreadsheets/d/1ennBAXi3vGJmvk8nBkmTqEtwCeNlRhh7pt3axqAmK3s/edit?usp=sharing'
sheet_week = 'https://docs.google.com/spreadsheets/d/19UQgj7yZD2BEPuuyAN9Vt7XPoxMkiJND_STV-ojX-ok/edit#gid=736077533'
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

def get_template(name, time, id, time_zone = 'по мск'):
    templates = [
        f'Добрый день, {name}!) \n\nНапоминаю про урок завтра в {time} {time_zone}! Буду ждать тебя)',
        f'Привет, {name}!) \n\nЖду тебя завтра на уроке в {time} {time_zone}!',
        f'Привет, {name}!💫 \n\nНе забудь про урок завтра в {time} {time_zone}! Жду тебя)😊',
        f'Здравствуй, {name}!\nНапоминаю о занятии завтра в {time} {time_zone}! Буду ждать тебя)',
        f'Привет, {name}!💫 Не забудь про урок завтра в {time} {time_zone}!)'

    ]
    return templates[id]

def get_template_for_group(time, id):
    templates = [
        f'Ребята, всем привет!\nЗавтра у нас состоится урок в {time} по мск! Всех буду ждать🌟\n\nНе забывайте про дз, если нужна помощь - пишите, буду рада помочь!😇',
        f'Привет всем, ребята!\n\nЗавтра у нас запланировано занятие в {time} по московскому времени! Жду всех с нетерпением🌟\n\nНе забудьте о домашнем задании, если вам нужна помощь - обращайтесь, я всегда готова помочь!😇',
        f'Привет всем!\n\nУ нас завтра состоится урок в {time} по мск! Всех жду🌟\nНе забывайте про дз, при необходимости обращайтесь, буду помогать!😇',
        f'Привет, ребята!\n\nЗавтра у нас урок в {time} по мск! Жду всех🌟\nНе забудьте о домашке, если что - обращайтесь, готова помочь!😇',
        f'Ребята, привет!\n\nЗавтра у нас запланирован урок в {time} по мск! Жду всех🌟\nНе забывайте про домашнее задание, если что-то не получается - обращайтесь, буду рада помочь!😇'
    ]
    return templates[id]

def get_contacts_dict():
    global sheet_info
    c = pygsheets.authorize(service_file='client_secret.json')
    sh_with_info = c.open_by_url(sheet_info)
    sh_kod = sh_with_info[0]
    sh_my = sh_with_info[1]
    res = {} # dict {names:contacts}
    for x in (sh_kod, sh_my):
        info = x.get_values_batch(['A:A', 'D:D'])
        for i in range(len(info[0])):
            
            if info[0][i] and info[1][i]: # если есть имя и контакт
                res[info[0][i][0]] = info[1][i][0]
    return res

# на будущее можно добавить код для проверки на чп моих учеников



def get_day_info(sheet_id = 0):
    global sheet_week
    c = pygsheets.authorize(service_file='client_secret.json')
    sh = c.open_by_url(sheet_week)
    wks = sh[sheet_id]
    dates = wks.get_values_batch(['C5:Z5'])[0][0]
    dates = [x for x in dates if x]
   
    days_column_id = ['C6:E35','F6:H35', 'J6:L35','M6:O35','Q6:S35', 'T6:V35', 'W6:Y35']
    # tomorrow = (datetime.today() + timedelta(days=1)).strftime('%d.%m.%Y')
    tomorrow = (datetime.today()).strftime('%d.%m.%Y')

    if tomorrow in dates:

        # данные для генерации шаблона: id - random
        id = randint(0,4)

        sheet_column_id = days_column_id[dates.index(tomorrow)]
        day = wks.get_values_batch(['B6:B35', sheet_column_id]) # two lists with dates and deals
        result = 'Твои планы на завтра:\n\n'
        plans = [] # список с сообщениями ученикам
        info_students = get_contacts_dict()
        for i, case in enumerate(day[1]):
            
            if case:
                
                time = day[0][i][0]
                name = case[0]
                result +=f'{time} - {name} \n'
                contact = info_students.get(name, 'нет контакта :(')

                if 'group' in name:
                    text_message = get_template_for_group(time, id)
                elif "нлайн" in name:
                    name = name.split()[1]
                    text_message = get_template(name, time, id)
                elif "Учен" in name:
                    name = name.split()[0]
                    time = str(int(time[:2])+2) + time[2:]
                    text_message = get_template(name, time, id,  '')
                    
                else:
                    continue

                messages = ['-'*20+f'\nУрок: {name} \nКонтакт: {contact}\nСообщение ученику:\n'+'-'*20, text_message]
                print(text_message)
                plans.append(messages)

        return '*'+result+'*', plans
    else:
        return text_error, {}


def get_deal_for_time(time, sheet_id = 0):
    global sheet_week
    c = pygsheets.authorize(service_file='client_secret.json')
    sh = c.open_by_url(sheet_week)
    wks = sh[sheet_id]
    dates = wks.get_values_batch(['C5:Z5'])[0][0]
    dates = [x for x in dates if x]
   
    days_column_id = ['C6:E35','F6:H35', 'J6:L35','M6:O35','Q6:S35', 'T6:V35', 'W6:Y35']
    today = datetime.today().strftime('%d.%m.%Y')

    if today in dates:

        sheet_column_id = days_column_id[dates.index(today)]
        day = wks.get_values_batch(['B6:B35', sheet_column_id]) # two lists with times and deals
        
        if [time] in day[0]:
            deal = day[1][day[0].index([time])]
            if deal:
                return f'В {time} у тебя будет {deal[0]}'

if __name__ == "__main__":

    # ----------------Это номер страницы с расписанием!!-----------------------------------
    sheet_id = get_sheet_id_with_star(sheet_week)
    # ----------------------------------------------------------------------

    text, list_mes = get_day_info(sheet_id)
    print(text)
    if text != text_error:
        for mes in list_mes:
            print(mes[0]) 
            print(mes[1])
