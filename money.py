from config import *

def get_data_by_column_from_money_sheet(sheet_id, batch):
    global SHEET_MONEY
    c = pygsheets.authorize(service_file='client_secret.json')
    sh = c.open_by_url(SHEET_MONEY)
    wks = sh[sheet_id]
    data = wks.get_values_batch(batch)
    return data

def get_id_of_date(sheet_id, day):
    global SHEET_MONEY
    c = pygsheets.authorize(service_file='client_secret.json')
    sh = c.open_by_url(SHEET_MONEY)
    wks = sh[sheet_id]
    data = wks.get_values_batch(['A:A'])[0]

    for i, x in enumerate(data):
        if x: data[i] = data[i][0]
        else: data[i] = ''

    return data.index(day)

# l - список с категориями (из таблицы)
# l2 - список с под-категориями (из таблицы)
# d - итоговый словарь
# id - это индекс разделителя (итого) id = l.index('итого')
# main_key - это ключ для словаря (income или expense)
# list - список с расходами или доходами (income или expense)
def make_dict(l, l2, d, id, main_key, list):

    for categ in list:
        if categ:
            categ_id = l.index(categ)
            d[main_key]['indexes'].append(categ_id)
            d[main_key]['categories'].append(categ)

    n = 0
    flag_id = d[main_key]['indexes'][n]
    while n < len(d[main_key]['indexes']):
        n+=1
        try:
            next_flag_id = d[main_key]['indexes'][n]
            subcategories = l2[flag_id:next_flag_id]
            d[main_key]['subcategories'].append(subcategories)
            if subcategories[0]:
                sub_indexes = []
                for x in subcategories:
                    sub_indexes.append(l2.index(x))
                d[main_key]['subindexes'].append(sub_indexes)
            else:
                # print(n-1)
                # print(d[main_key]['categories'])
                d[main_key]['subindexes'].append([l.index(d[main_key]['categories'][n-1])])
                # print(l.index(d[main_key]['categories'][n-1]))
                # print(d[main_key]['categories'][n-1])
                # print('\n')
            flag_id = next_flag_id
        except IndexError:
            d[main_key]['subcategories'].append(l2[flag_id:id])
            subcategories = l2[flag_id:id]
            if subcategories[0]:
                sub_indexes = []
                for x in subcategories:
                    sub_indexes.append(l2.index(x))
                d[main_key]['subindexes'].append(sub_indexes)
            else:
                d[main_key]['subindexes'].append([l.index(d[main_key]['categories'][n-1])])

    return d


def create_dict_with_data(l,l2):
    id = l.index('итого')
    id_2 = l[id+1:].index('итого')+id+1

    income = l[2:id]
    expense = l[id+1:id_2]

    d = {
        'income':{
            'indexes':[],
            'categories':[],
            'subcategories':[],
            'subindexes':[]
        },
        'expense':{
            'indexes':[],
            'categories':[],
            'subcategories':[],
            'subindexes':[]
        }
        }
    d = make_dict(l, l2, d, id, 'income', income)
    d = make_dict(l, l2, d, id_2, 'expense', expense)
    return d


def return_addr(row, column):# row - строка , column - номер столбца
    letters = [ let for let in string.ascii_uppercase]
    letters += [ 'A'+let for let in string.ascii_uppercase]
    addr = letters[column] + str(row)
    return addr

def update_value_in_sheet(sheet_id, addr, value): # addr = (row,column)
    global SHEET_MONEY
    c = pygsheets.authorize(service_file='client_secret.json')
    sh = c.open_by_url(SHEET_MONEY)
    wks = sh[sheet_id]
    if wks.get_value(addr).isdigit():
        value = int(wks.get_value(addr))+value
    wks.update_value(addr, value)


if __name__ == "__main__":
    # ----------------Это номер страницы с расписанием!!-----------------------------------
    sheet_id = get_sheet_id_with_star(SHEET_MONEY)
    # ----------------------------------------------------------------------
    categories_list, subcategories_list  = get_data_by_column_from_money_sheet(sheet_id, ['1:2'])[0]
    result_dict = create_dict_with_data(categories_list, subcategories_list)

    today = str(int((datetime.today()+ timedelta(hours=3)).strftime('%d')))
    str_id = get_id_of_date(sheet_id, today) # номер строки в которую нужно будет внести запись


    while True:
        input_0 = int(input("Scolko?"))


        # 1 quest: keyboard
        print('# 1 quest: keyboard')
        input_1 = input('income or expense? ')
        print(result_dict[input_1]['categories'])

        # 2 quest: keyboard
        print('# 2 quest: keyboard')
        input_2 = input('which one? ')
        i = result_dict[input_1]['categories'].index(input_2) # index of value in list

        subcats = result_dict[input_1]['subcategories'][i]
        if subcats[0]:
            print(subcats)

            # 3 input: keyboard
            print('# 3 input: keyboard')
            input_3 = input('which one? ')
            # print(result_dict[input_1]['subindexes'])
            res_id_in_main_dict = result_dict[input_1]['subindexes'][i][subcats.index(input_3)]
        else:
            res_id_in_main_dict = result_dict[input_1]['indexes'][i]

        print(res_id_in_main_dict)
        print(categories_list[res_id_in_main_dict])
        print(subcategories_list[res_id_in_main_dict])
        addr = return_addr(str_id+1, res_id_in_main_dict)
        update_value_in_sheet(sheet_id, addr, input_0)



