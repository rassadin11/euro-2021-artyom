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

date = datetime.datetime.today() + timedelta(hours = 3)

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
    itembtn5 = types.KeyboardButton("С каким счетом сыграла...")

    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)

    bot.send_message(message.chat.id, "Что хотите узнать?", reply_markup = markup)
    
@bot.message_handler(content_types=['text'])

def send_matches(message):
    match = []
    array_of_dates = []

    if message.text == 'Матчи на сегодня':
        match = parse()

        dt = '{}:{}:{}'.format(date.hour, date.minute, date.second)
        dt_year = '{}-{}-{}'.format(date.year, date.month, date.day)
        
        for m in match:
            if (m['date'] == date.strftime('%Y-%m-%d')) and (date.strptime(m['time'], '%H:%M:%S') > date.strptime(dt, '%H:%M:%S')):
                array_of_dates.append(m)
                continue

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
        bot.send_message(message.chat.id, "Выбери команду", reply_markup = markup_inline)

    elif message.text == 'С каким счетом сыграла...':
        markup = types.InlineKeyboardMarkup(row_width = 2)

        itembtn1 = types.InlineKeyboardButton('Португалия 🇵🇹', callback_data = 'Португалия_1')
        itembtn2 = types.InlineKeyboardButton('Франция 🇫🇷', callback_data = 'Франция_1')
        itembtn3 = types.InlineKeyboardButton('Германия 🇩🇪', callback_data = 'Германия_1')
        itembtn4 = types.InlineKeyboardButton('Бельгия 🇧🇪', callback_data = 'Бельгия_1')
        itembtn5 = types.InlineKeyboardButton('Уэльс 🏴󠁧󠁢󠁷󠁬󠁳󠁿', callback_data = 'Уэльс_1')
        itembtn6 = types.InlineKeyboardButton('Дания 🇩🇰', callback_data = 'Дания_1')
        itembtn7 = types.InlineKeyboardButton('Италия 🇮🇹', callback_data = 'Италия_1')
        itembtn8 = types.InlineKeyboardButton('Австрия 🇦🇹', callback_data = 'Австрия_1')
        itembtn9 = types.InlineKeyboardButton('Нидерланды 🇳🇱', callback_data = 'Нидерланды_1')
        itembtn10 = types.InlineKeyboardButton('Чехия 🇨🇿', callback_data = 'Чехия_1')
        itembtn11 = types.InlineKeyboardButton('Хорватия 🇭🇷', callback_data = 'Хорватия_1')
        itembtn12 = types.InlineKeyboardButton('Испания 🇪🇸', callback_data = 'Испания_1')
        itembtn13 = types.InlineKeyboardButton('Швейцария 🇨🇭', callback_data = 'Швейцария_1')
        itembtn14 = types.InlineKeyboardButton('Англия 🏴󠁧󠁢󠁥󠁮󠁧󠁿', callback_data = 'Англия_1')
        itembtn15 = types.InlineKeyboardButton('Швеция 🇸🇪', callback_data = 'Швеция_1')
        itembtn16 = types.InlineKeyboardButton('Украина 🇺🇦', callback_data = 'Украина_1')

        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8, itembtn9, itembtn10, itembtn11, itembtn12, itembtn13, itembtn14, itembtn15, itembtn16)
        bot.send_message(message.chat.id, "Выбери команду. Выведится сообщение с последним сыгранным матчем этой команды на EURO-2021", reply_markup = markup)

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

        if call.data == 'Португалия_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Франция_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Германия_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Бельгия_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Уэльс_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Дания_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Италия_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Австрия_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Нидерланды_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Чехия_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Хорватия_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Испания_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Швейцария_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Англия_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Швеция_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

        if call.data == 'Украина_1':
            name = call.data.split("_")[0]
            match = parse()
            dtt = '{}-{}-{}'.format(date.year, date.month, date.day)
            datetime = date.strptime(dtt, '%Y-%m-%d')
            i = 0

            def recursive_function(data):

                new_date = data.strftime("%Y-%m-%d")
                for m in match:
                    if m['date'] == new_date:
                        for team in m['teams']:
                            if team == name:
                                number = date.strptime(m['date'], '%Y-%m-%d')
                                numb = '{}'.format(number.day)
                                month = number.strftime('%B')

                                dictionary_month = {
                                    'January': 'Января', 
                                    'Fabruary': 'Февраля',
                                    'March': 'Марта',
                                    'April': 'Апреля',
                                    'May': 'Мая',
                                    'June': 'Июня',
                                    'July': 'Июля', 
                                    'August': 'Августа',
                                    'September': 'Сентября',
                                    'Octember': 'Октября',
                                    'November': 'Ноября',
                                    'December': 'Декабря',
                                }

                                month = dictionary_month[month]

                                bot.send_message(call.message.chat.id, '{} - {}. {}-{}. Игра проходила {} {}'.format(m['teams'][0], m['teams'][1], m['score'][0], m['score'][1], numb, month))
                                return
                i = 0
                i += 1
                recursive_function(data + timedelta(days = -i))

            recursive_function(datetime)

bot.polling(none_stop = True)
