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
        date = item.find('div', class_ = 'match-teaser__info').get_text(strip = True).replace('Чемпионат Европы. ', '').replace(' Не начался', '')
        data_array = date.split(' ');

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

bot = telebot.TeleBot("1822822709:AAEG9BlP6pvHWeaa1jcEE0QaM5xFwlfIikM")

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
            if m['date'] == datetime.datetime.today().strftime('%Y-%m-%d'):
                array_of_dates.append(m)

        if len(array_of_dates) == 0:
            bot.send_message(message.chat.id, 'Сегодня нет ни одного матча')
        else:
            if len(array_of_dates) > 1:
                to_send_message = '''Сегодня будет несколько матчей'''
                bot.send_message(message.chat.id, to_send_message)

                for game in array_of_dates:
                    g = '''Игра будет между {} и {}. Игра начнется в {}'''.format(game['teams'][0], game['teams'][1], game['time'])
                    bot.send_message(message.chat.id, g)

            if len(array_of_dates) == 1:
                to_send_message = '''Сегодня будет матч'''
                game = '''Игра будет между {} и {}. Игра начнется в {}'''.format(array_of_dates[0]['teams'][0], array_of_dates[0]['teams'][1], array_of_dates[0]['time'])
                bot.send_message(message.chat.id, to_send_message)
                bot.send_message(message.chat.id, game)

    elif message.text == 'Матчи на завтра':
        match = parse()

        for m in match:
            dtt = datetime.datetime.today()
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
                    g = '''Игра будет между {} и {}. Игра начнется в {}'''.format(game['teams'][0], game['teams'][1], game['time'])
                    bot.send_message(message.chat.id, g)

            if len(array_of_dates) == 1:
                to_send_message = '''Завтра будет матч'''
                game = '''Игра будет между {} и {}. Игра начнется в {}'''.format(array_of_dates[0]['teams'][0], array_of_dates[0]['teams'][1], array_of_dates[0]['time'])
                bot.send_message(message.chat.id, to_send_message)
                bot.send_message(message.chat.id, game)

    elif message.text == 'Ближайшие матчи':
        match = parse()
        i = 2

        while len(array_of_dates) == 0:
            for m in match:
                dtt = datetime.datetime.today()
                dtt = dtt + timedelta(days = i)
                
                if m['date'] == dtt.strftime('%Y-%m-%d'):
                    array_of_dates.append(m)

            i += 1

        match = []
        word = num_word(i, ['день', 'дня', 'дней'])

        if len(array_of_dates) > 0:
            if len(array_of_dates) > 1:
                to_send_message = '''Через {} {} будет несколько матчей'''.format(i, word)
                bot.send_message(message.chat.id, to_send_message)

                for game in array_of_dates:
                    g = '''Игра будет между {} и {}. Игра начнется в {}'''.format(game['teams'][0], game['teams'][1], game['time'])
                    bot.send_message(message.chat.id, g)

            if len(array_of_dates) == 1:
                to_send_message = '''Через {} {} будет матч'''.format(i, word)
                game = '''Игра будет между {} и {}. Игра начнется в {}'''.format(array_of_dates[0]['teams'][0], array_of_dates[0]['teams'][1], array_of_dates[0]['time'])
                bot.send_message(message.chat.id, to_send_message)
                bot.send_message(message.chat.id, game)

    elif message.text == 'С кем будет играть...':
        markup = types.ReplyKeyboardMarkup(row_width = 2)

        itembtn1 = types.KeyboardButton('Португалия')
        itembtn2 = types.KeyboardButton('Франция')
        itembtn3 = types.KeyboardButton('Германия')
        itembtn4 = types.KeyboardButton('Бельгия')
        itembtn5 = types.KeyboardButton('Уэльс')
        itembtn6 = types.KeyboardButton('Дания')
        itembtn7 = types.KeyboardButton('Италия')
        itembtn8 = types.KeyboardButton('Австрия')
        itembtn9 = types.KeyboardButton('Нидерланды')
        itembtn10 = types.KeyboardButton('Чехия')
        itembtn11 = types.KeyboardButton('Хорватия')
        itembtn12 = types.KeyboardButton('Испания')
        itembtn13 = types.KeyboardButton('Швейцария')
        itembtn14 = types.KeyboardButton('Англия')
        itembtn15 = types.KeyboardButton('Швеция')
        itembtn16 = types.KeyboardButton('Украина')

        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8, itembtn9, itembtn10, itembtn11, itembtn12, itembtn13, itembtn14, itembtn15, itembtn16)
        bot.send_message(message.chat.id, "Выбери команду. Для того, чтобы вернуться обратно напиши: /comeback", reply_markup = markup)

    else:
        array = message.text.split(' ')

        if len(array) > 0:
            country = array[0]
            match = parse()
            date = datetime.datetime.today()
            temporary_name = False

            for game in match:
                for m in game['teams']:
                    if (m == country) and (game['date'] > date.strftime('%Y-%m-%d')):
                        if len(game['teams']) == 2:
                            bot.send_message(message.chat.id, '{} - {}'.format(game['teams'][0], game['teams'][1]))

                        if len(game['teams']) == 1:
                            bot.send_message(message.chat.id, 'Еще не известно с кем будет играть {}'.format(game['teams'][0]))

                        temporary_name = True

            if temporary_name == False:
                bot.send_message(message.chat.id, '{} уже не будет играть на EURO-2021. Сочувствую'.format(country))

bot.polling(none_stop = True)