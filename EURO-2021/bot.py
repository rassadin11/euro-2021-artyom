import requests
import datetime 
import telebot
from telebot import types
import math
from datetime import timedelta
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

URL = 'https://www.sports.ru/uefa-euro/calendar/'

total_info = []
all_countries = ['Португалия', "Бельгия", "Франция", "Германия", "Дания", "Уэльс", "Италия", "Австрия", "Нидерланды", "Чехия", "Хорватия", "Испания", "Швейцария", "Англия", "Швеция", "Украина"]

declension_of_words = {
    "Португалия": "Португалией",
    "Бельгия": "Бельгией",
    "Франция": "Францией",
    "Германия": "Германией",
    "Дания": "Португалией",
    "Уэльс": "Уэльсом",
    "Италия": "Италией",
    "Австрия": "Австрией",
    "Нидерланды": "Нидерландами",
    "Чехия": "Чехией",
    "Хорватия": "Хорватией",
    "Испания": "Испанией",
    "Швейцария": "Швейцарией",
    "Англия": "Англией",
    "Швеция": "Швецией",
    "Украина": "Украиной",    
}

date = datetime.datetime.today()

def num_word(value, words):
    value = value % 100
    num = value % 10

    if (value > 10) and (value < 20):
        return words[2]

    if (num > 1) and (num < 5):
        return words[1]

    if num == 1:
        return words[0]

    return words[2]

def parse():

    ua = UserAgent()

    HEADERS = {
        'User-Agent': ua.random
    }
    
    response = requests.get(URL, headers = HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.findAll('div', class_ = 'match-teaser match-schedule-column__matches-item')
    
    total_info = []
    
    for item in items:
        teams = item.findAll('span', class_ = 'match-teaser__team-name')
        name_team = []

        for team in teams:
            name_team.append(team.get_text(strip = True))

        score = item.find('div', class_ = 'match-teaser__team-score').get_text(strip = True).replace('–', ' ')
        match_date = item.find('div', class_ = 'match-teaser__info').get_text(strip = True).replace('Чемпионат Европы. ', '').replace(' Не начался', '')
        data_array = match_date.split(' ');

        real_date = data_array[0][0:-1].split(".")
        real_date = list(reversed(real_date))
        real_date = '-'.join(real_date)
        real_time = data_array[1].replace('.', '') + ':00'
        rl_t = datetime.datetime.strptime(real_time, '%H:%M:%S') + timedelta(hours = 3)
        rl_d = datetime.datetime.strptime(real_date, '%Y-%m-%d')

        total_info.append({
            'teams': name_team,
            'score': score.split(' '),
            'date': rl_d.strftime('%Y-%m-%d'),
            'time': rl_t.strftime('%H:%M:%S')
        })

    return total_info

bot = telebot.TeleBot("1822822709:AAEG9BlP6pvHWeaa1jcEE0QaM5xFwlfIikM") # 1822822709:AAEG9BlP6pvHWeaa1jcEE0QaM5xFwlfIikM, 1808668238:AAEFTKkXNnXvgLZ2bXD1NgbLEf8CAbzaFd8

@bot.message_handler(commands=['start'])

def send_echo(message):
    markup = types.ReplyKeyboardMarkup(row_width = 2)

    itembtn1 = types.KeyboardButton('Матчи на сегодня')
    itembtn2 = types.KeyboardButton('Матчи на завтра')
    itembtn3 = types.KeyboardButton('Ближайшие матчи')
    itembtn4 = types.KeyboardButton('С кем будет играть...')

    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)

    bot.send_message(message.chat.id, "Что хотите узнать?", reply_markup = markup)

@bot.message_handler(commands=['comeback'])

def comeback_to_choise(message):
    markup = types.ReplyKeyboardMarkup(row_width = 2)

    itembtn1 = types.KeyboardButton('Матчи на сегодня')
    itembtn2 = types.KeyboardButton('Матчи на завтра')
    itembtn3 = types.KeyboardButton('Ближайшие матчи')
    itembtn4 = types.KeyboardButton('С кем будет играть...')

    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)

    bot.send_message(message.chat.id, "Что хотите узнать?", reply_markup = markup)
    
@bot.message_handler(content_types=['text'])

def send_matches(message):
    match = []
    array_of_dates = []

    if message.text == 'Матчи на сегодня':
        match = parse()
        
        for m in match:
            if (m['date'] == date.strftime('%Y-%m-%d')): # and (m['time'] > date.strftime('%H:%M:%S'))
                array_of_dates.append(m)

        if len(array_of_dates) == 0:
            bot.send_message(message.chat.id, 'Сегодня нет ни одного матча')
        else:
            if len(array_of_dates) > 1:
                to_send_message = '''Сегодня будет несколько матчей'''
                bot.send_message(message.chat.id, to_send_message)

                for game in array_of_dates:
                    first_country = declension_of_words[game['teams'][0]]
                    second_country = declension_of_words[game['teams'][1]]

                    g = '''Игра будет между {} и {}. Игра начнется в {}'''.format(first_country, second_country, game['time'])
                    bot.send_message(message.chat.id, g)

            if len(array_of_dates) == 1:
                to_send_message = '''Сегодня будет матч'''
                first_country = declension_of_words['{}'.format(array_of_dates[0]['teams'][0])]
                second_country = declension_of_words['{}'.format(array_of_dates[0]['teams'][1])]

                game = '''Игра будет между {} и {}. Игра начнется в {}'''.format(first_country, second_country, array_of_dates[0]['time'])
                bot.send_message(message.chat.id, to_send_message)
                bot.send_message(message.chat.id, game)

    elif message.text == 'Матчи на завтра':
        match = parse()

        for m in match:
            dtt = date
            dtt = dtt + timedelta(days = 1)

            if m['date'] == dtt.strftime('%Y-%m-%d'):
                array_of_dates.append(m)

        if len(array_of_dates) == 0:
            bot.send_message(message.chat.id, 'Завтра не будет ни одного матча')
        else:
            if len(array_of_dates) > 1:
                to_send_message = '''Завтра будет несколько матчей'''
                bot.send_message(message.chat.id, to_send_message)

                for game in array_of_dates:
                    first_country = declension_of_words[game['teams'][0]]
                    second_country = declension_of_words[game['teams'][1]]
                    
                    g = '''Игра будет между {} и {}. Игра начнется в {}'''.format(first_country, second_country, game['time'])
                    bot.send_message(message.chat.id, g)

            if len(array_of_dates) == 1:
                to_send_message = '''Завтра будет матч'''
                first_country = declension_of_words[array_of_dates[0]['teams'][0]]
                second_country = declension_of_words[array_of_dates[0]['teams'][1]]

                game = '''Игра будет между {} и {}. Игра начнется в {}'''.format(first_country, second_country, array_of_dates[0]['time'])
                bot.send_message(message.chat.id, to_send_message)
                bot.send_message(message.chat.id, game)

    elif message.text == 'Ближайшие матчи':
        match = parse()
        i = 0

        while len(array_of_dates) == 0:
            temporary_value = False

            for m in match:
                dtt = date
                dtt = dtt + timedelta(days = i)
                print(m['date'], dtt.strftime('%Y-%m-%d'))
                if m['date'] == dtt.strftime('%Y-%m-%d'):
                    array_of_dates.append(m)
                    temporary_value = True

            if temporary_value == False:
                i += 1
            else:
                break

        match = []
        word = num_word(i, ['день', 'дня', 'дней'])

        if len(array_of_dates) > 0:
           if i == 0:
               to_send_message = '''Сегодня будет несколько матчей'''
               bot.send_message(message.chat.id, to_send_message)

           if i == 1:
               to_send_message = '''Завтра будет несколько матчей'''
               bot.send_message(message.chat.id, to_send_message)

           if i >= 2:
               to_send_message = '''Через {} {} будет несколько матчей'''.format(i, word)
               bot.send_message(message.chat.id, to_send_message)

           for game in array_of_dates:
               first_country = declension_of_words[game['teams'][0]]
               second_country = declension_of_words[game['teams'][1]]
               
               g = '''Игра будет между {} и {}. Игра начнется в {}'''.format(first_country, second_country, game['time'])
               bot.send_message(message.chat.id, g)

        if len(array_of_dates) == 1:
            to_send_message = '''Через {} {} будет матч'''.format(i, word)
            first_country = declension_of_words[array_of_dates[0]['teams'][0]]
            second_country = declension_of_words[array_of_dates[0]['teams'][1]]

            game = '''Игра будет между {} и {}. Игра начнется в {}'''.format(first_country, second_country, array_of_dates[0]['time'])
            bot.send_message(message.chat.id, to_send_message)
            bot.send_message(message.chat.id, game)

    elif message.text == 'С кем будет играть...':
        markup_inline = types.InlineKeyboardMarkup(row_width = 2)

        itembtn1 = types.InlineKeyboardButton('Португалия 🇵🇹', callback_data = 'Португалия')
        itembtn2 = types.InlineKeyboardButton('Франция 🇫🇷', callback_data = 'Франция')
        itembtn3 = types.InlineKeyboardButton('Германия 🇩🇪', callback_data = 'Германия')
        itembtn4 = types.InlineKeyboardButton('Бельгия 🇧🇪', callback_data = 'Бельгия')
        itembtn5 = types.InlineKeyboardButton('Уэльс 🏴󠁧󠁢󠁷󠁬󠁳󠁿', callback_data = 'Уэльс')
        itembtn6 = types.InlineKeyboardButton('Дания 🇩🇰', callback_data = 'Дания')
        itembtn7 = types.InlineKeyboardButton('Италия 🇮🇹', callback_data = 'Италия')
        itembtn8 = types.InlineKeyboardButton('Австрия 🇦🇹', callback_data = 'Австрия')
        itembtn9 = types.InlineKeyboardButton('Нидерланды 🇳🇱', callback_data = 'Нидерланды')
        itembtn10 = types.InlineKeyboardButton('Чехия 🇨🇿', callback_data = 'Чехия')
        itembtn11 = types.InlineKeyboardButton('Хорватия 🇭🇷', callback_data = 'Хорватия')
        itembtn12 = types.InlineKeyboardButton('Испания 🇪🇸', callback_data = 'Испания')
        itembtn13 = types.InlineKeyboardButton('Швейцария 🇨🇭', callback_data = 'Швейцария')
        itembtn14 = types.InlineKeyboardButton('Англия 🏴󠁧󠁢󠁥󠁮󠁧󠁿', callback_data = 'Англия')
        itembtn15 = types.InlineKeyboardButton('Швеция 🇸🇪', callback_data = 'Швеция')
        itembtn16 = types.InlineKeyboardButton('Украина 🇺🇦', callback_data = 'Украина')

        markup_inline.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8, itembtn9, itembtn10, itembtn11, itembtn12, itembtn13, itembtn14, itembtn15, itembtn16)
        bot.send_message(message.chat.id, "Выбери команду. Для того, чтобы вернуться обратно напиши: /comeback", reply_markup = markup_inline)

    # elif message.text == 'С каким счетом сыграла...':
    #     itembtn1 = types.KeyboardButton('Португалия')
    #     itembtn2 = types.KeyboardButton('Франция')
    #     itembtn3 = types.KeyboardButton('Германия')
    #     itembtn4 = types.KeyboardButton('Бельгия')
    #     itembtn5 = types.KeyboardButton('Уэльс')
    #     itembtn6 = types.KeyboardButton('Дания')
    #     itembtn7 = types.KeyboardButton('Италия')
    #     itembtn8 = types.KeyboardButton('Австрия')
    #     itembtn9 = types.KeyboardButton('Нидерланды')
    #     itembtn10 = types.KeyboardButton('Чехия')
    #     itembtn11 = types.KeyboardButton('Хорватия')
    #     itembtn12 = types.KeyboardButton('Испания')
    #     itembtn13 = types.KeyboardButton('Швейцария')
    #     itembtn14 = types.KeyboardButton('Англия')
    #     itembtn15 = types.KeyboardButton('Швеция')
    #     itembtn16 = types.KeyboardButton('Украина')

    #     markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8, itembtn9, itembtn10, itembtn11, itembtn12, itembtn13, itembtn14, itembtn15, itembtn16)
    #     bot.send_message(message.chat.id, "Выбери команду. Для того, чтобы вернуться обратно напиши: /comeback", reply_markup = markup)

@bot.callback_query_handler(func=lambda call:True)

def callback(call):
    if call.message:
        if call.data == 'Португалия':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021'.format(country))
                        return

        if call.data == 'Франция':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

        if call.data == 'Германия':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

        if call.data == 'Бельгия':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

        if call.data == 'Уэльс':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

        if call.data == 'Дания':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return  

        if call.data == 'Италия':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

        if call.data == 'Австрия':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

        if call.data == 'Нидерланды':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

        if call.data == 'Чехия':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

        if call.data == 'Хорватия':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

        if call.data == 'Испания':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

        if call.data == 'Швейцария':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

        if call.data == 'Англия':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

        if call.data == 'Швеция':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

        if call.data == 'Украина':
            for country in all_countries:
                if call.data == country:
                    match = parse()
                    temporary_name = False

                    for game in match:
                        for m in game['teams']:
                            if (m == country) and (game['date'] >= date.strftime('%Y-%m-%d')):
                                if len(game['teams']) == 2:
                                    bot.send_message(call.message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))
                                    return

                                    temporary_name = True

                    if temporary_name == False:
                        bot.send_message(call.message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))
                        return

bot.polling(none_stop = True)
