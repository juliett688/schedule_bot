from config import *

def get_template(name, time, id, time_zone = 'по мск', today = False):
    templates = [
        f'Добрый день, {name}!) \n\nНапоминаю про урок {"сегодня" if today else "завтра"} в {time} {time_zone}! Буду ждать тебя)',
        f'Привет, {name}!) \n\nЖду тебя {"сегодня" if today else "завтра"} на уроке в {time} {time_zone}!',
        f'Привет, {name}!💫 \n\nНе забудь про урок {"сегодня" if today else "завтра"} в {time} {time_zone}! Жду тебя)😊',
        f'Здравствуй, {name}!\nНапоминаю о занятии {"сегодня" if today else "завтра"} в {time} {time_zone}! Буду ждать тебя)',
        f'Привет, {name}!💫 Не забудь про урок {"сегодня" if today else "завтра"} в {time} {time_zone}!)'
    ]
    return templates[id]

def get_template_for_parents(parent_name, name, time, id, time_zone = 'по мск', today = False):
    templates = [
        f'Добрый день, {parent_name}!) \n\nНапоминаю про урок {"сегодня" if today else "завтра"} с {name} в {time} {time_zone}! Буду ждать его)',
        f'Добрый день, {parent_name}!) \n\nЖду {name} {"сегодня" if today else "завтра"} на уроке в {time} {time_zone}!',
        f'Здравствуйте, {parent_name}!\nНапоминаю о занятии с {name} {"сегодня" if today else "завтра"} в {time} {time_zone}!)'
    ]
    return templates[id]

def get_template_for_group(time, id, today = False):
    templates = [
        f'Ребята, всем привет!\{"Cегодня" if today else "Завтра"} у нас состоится урок в {time} по мск! Всех буду ждать🌟\n\nНе забывайте про дз, если нужна помощь - пишите, буду рада помочь!😇',
        f'Привет всем, ребята!\n\{"Сегодня" if today else "Завтра"} у нас запланировано занятие в {time} по московскому времени! Жду всех с нетерпением🌟\n\nНе забудьте о домашнем задании, если вам нужна помощь - обращайтесь, я всегда готова помочь!😇',
        f'Привет всем!\n\nУ нас {"сегодня" if today else "завтра"} состоится урок в {time} по мск! Всех жду🌟\nНе забывайте про дз, при необходимости обращайтесь, буду помогать!😇',
        f'Привет, ребята!\n\{"Сегодня" if today else "Завтра"} у нас урок в {time} по мск! Жду всех🌟\nНе забудьте о домашке, если что - обращайтесь, готова помочь!😇',
        f'Ребята, привет!\n\{"Сегодня" if today else "Завтра"} у нас запланирован урок в {time} по мск! Жду всех🌟\nНе забывайте про домашнее задание, если что-то не получается - обращайтесь, буду рада помочь!😇'
    ]
    return templates[id]

def get_contacts_dict():
    """
    return res: list [ 
                        {
                            "name" : name,
                            "contact" : contact,
                            "parent_name" : parent_name,
                            "parent_contact" : parent_contact
                        }
                                
                     ]
    
    """
    global SHEET_INFO
    c = pygsheets.authorize(service_file='client_secret.json')
    sh_with_info = c.open_by_url(SHEET_INFO)
    sh_kod = sh_with_info[0]
    sh_my = sh_with_info[1]
    res = {} 
    for x in (sh_kod, sh_my):
        info = x.get_values_batch(['A:A', 'D:D'])
        for i in range(len(info[0])):
            
            if info[0][i] and info[1][i]: # если есть имя и контакт
                res[info[0][i][0]] = info[1][i][0]
    return res

# на будущее можно добавить код для проверки на чп моих учеников

def get_day_info(sheet_id = 0, today = False):
    global SHEET_WEEK
    c = pygsheets.authorize(service_file='client_secret.json')
    sh = c.open_by_url(SHEET_WEEK)
    wks = sh[sheet_id]
    dates = wks.get_values_batch(['C5:Z5'])[0][0]
    dates = [x for x in dates if x]
   
    days_column_id = ['C6:E35','F6:H35', 'J6:L35','M6:O35','Q6:S35', 'T6:V35', 'W6:Y35']
    
    # Проверка на отправку уведомлений на сегодня или завтра
    if today: tomorrow = (datetime.today()).strftime('%d.%m.%Y')
    else: tomorrow = (datetime.today() + timedelta(days=1)).strftime('%d.%m.%Y')
    
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
                    text_message = get_template_for_group(time, id, today=today)
                elif "нлайн" in name:
                    name = name.split()[1]
                    text_message = get_template(name, time, id, today=today)
                    
                elif "Учен" in name:
                    name = name.split()[0]
                    time = str(int(time[:time.find(':')])+2) + time[time.find(':'):]
                    text_message = get_template(name, time, id,  '', today=today)
                    
                else:
                    continue

                messages = ['-'*20+f'\nУрок: {name} \nКонтакт: {contact}\nСообщение ученику:\n'+'-'*20, text_message]
                print(text_message)
                plans.append(messages)

        return '*'+result+'*', plans
    else:
        return TEXT_ERROR, {}


def get_deal_for_time(time, sheet_id = 0):
    global SHEET_WEEK
    sheet_id = get_sheet_id_with_star(SHEET_WEEK)
    dict_deals = get_dict_time_deals(sheet_id, (datetime.today()+ timedelta(hours=3)).strftime('%d.%m.%Y'))
    if dict_deals == TEXT_ERROR:
        return TEXT_ERROR
    if time in dict_deals.keys():
        return f'В {time} у тебя будет {dict_deals[time]}'
    
def get_dict_time_deals(sheet_id = 0, day = (datetime.today()+ timedelta(hours=3)).strftime('%d.%m.%Y') ):  # time: deal
    global SHEET_WEEK
    c = pygsheets.authorize(service_file='client_secret.json')
    sh = c.open_by_url(SHEET_WEEK)
    wks = sh[sheet_id]
    dates = wks.get_values_batch(['C5:Z5'])[0][0]
    dates = [x for x in dates if x]

    days_column_id = ['C6:E35','F6:H35', 'J6:L35','M6:O35','Q6:S35', 'T6:V35', 'W6:Y35']

    if day in dates:
        sheet_column_id = days_column_id[dates.index(day)]
        day = wks.get_values_batch(['B6:B35', sheet_column_id]) # two lists with dates and deals
        dict_plans = {} # time: deal
        for i, case in enumerate(day[1]):
            if case:
                time = day[0][i][0]
                name = case[0]
                dict_plans[time] = name
        return dict_plans
    else:
        return TEXT_ERROR
    
def get_next_deal():
    try:
        global SHEET_WEEK
        sheet_id = get_sheet_id_with_star(SHEET_WEEK)
        dict_deals = get_dict_time_deals(sheet_id, (datetime.today()+ timedelta(hours=3)).strftime('%d.%m.%Y'))
        now = (datetime.now()+ timedelta(hours=3)).strftime("%H:%M")
        times = list(dict_deals.keys())
        i = 0
        while now>times[i+1]:
            if i+2 == len(times): return 'Больше дел на сегодня нет'
            i += 1
        time_deal = times[i+1]
        return f'Ближайшее дело сегодня в *{time_deal}* - *{dict_deals[time_deal]}*'
    except:
        return TEXT_ERROR