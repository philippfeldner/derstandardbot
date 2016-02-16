import re
import time
import urllib.request
import urllib.error

import telegram
from telelib import tele
from telelib import admin

ADMIN_ID = 19965814


# This function uses a time_trigger
# to send the daily news at
# a specified time to all subscribers
def sub_service(bot):
    if tele.time_trigger(admin.send_time(1)) or tele.time_trigger(admin.send_time(2)):
        tele.send_to_subscriber(bot, generate_news_message('/news'))


# Fetches the news using urllib.request
# returns a tuples of URLs and headlines
# Potentially gets stuck in loop when internet issues
def get_news(news, topic=''):
    re_url = ''
    re_title = ''
    link = ''
    if news == 'derstandard':
        link = 'http://derstandard.at' + '/' + topic
        re_url = r'<h3><a href="(.*?)"'
        re_title = r'<h3><a href=".*?">(.*?)<'

    while True:
        try:
            source = urllib.request.urlopen(link)
            break
        except urllib.error.URLError:
            if (int(time.strftime('%M')) % 5) == 0:
                print('Connectivity Issues')
            time.sleep(4)

    der_standard = source.read().decode('utf-8')
    title = re.findall(re_title, der_standard, re.DOTALL)
    url = re.findall(re_url, der_standard, re.DOTALL)
    return url, title


# Creates the actual message to be send to the user
# analyses the message for additional parameters
# which define the amount of headline the user wants.
def generate_news_message(message):
    parameter = re.findall(r'\d+', message)
    mtime = time.strftime('%X')[:5]
    mdate = time.strftime('%d.%m.%y')

    reply = mdate + ' - ' + mtime + '\n'
    reply += '<b>Die momentanen Schlagzeilen auf derstandard.at:</b> \n\n'
    link, title = get_news('derstandard')
    for i in range(len(link)):
        link[i] = 'http://derstandard.at' + link[i]

    if parameter == [] or len(parameter) > 1 or int(parameter[0]) < 1:
        request = 5
    elif int(parameter[0]) > 30:
        request = 30
    else:
        request = int(parameter[0])

    for i in range(request):
        reply += ('<a href="' + link[i] + '">' + title[i] + '</a>' + '\n' + '------------------------------\n')

    if '<span class="ugc-icon">#</span>' in reply:
        reply = reply.replace('<span class="ugc-icon">#</span>', '')
    return reply


# The topic handler fetches
# news and processes it. It
# also sends it to the user.
def topic_handler(bot, message, chat_id):
    mtime = time.strftime('%X')[:5]
    mdate = time.strftime('%d.%m.%y')
    link = []
    headline = []

    reply = mdate + ' - ' + mtime + '\n'
    reply += '<b>Die Schlagzeilen zum Thema ' + message + '!</b>:' + ' \n\n'

    while True:
        try:
            source = urllib.request.urlopen('http://derstandard.at/' + message)
            break
        except urllib.error.URLError:
            if (int(time.strftime('%M')) % 5) == 0:
                print('Connectivity Issues')
            time.sleep(4)

    derstandard = source.read().decode('utf-8')
    regex = r'<h3><a href="(.*?)">(.*?)<'
    match = re.findall(regex, derstandard, re.DOTALL)

    for i in range(len(match)):
        if match[i][0] == [] or match[i][1] == []:
            match.pop(i)
    for i in range(len(match)):
        link.append('http://derstandard.at' + match[i][0])
        headline.append(match[i][1])

    for i in range(0, 5):
        reply += ('<a href="' + link[i] + '">' + headline[i] + '</a>' + '\n' +
                  '------------------------------\n')

    if '<span class="ugc-icon">#</span>' in reply:
        reply = reply.replace('<span class="ugc-icon">#</span>', '')
    reply_markup = telegram.ReplyKeyboardHide()
    admin.news_call()
    text = 'NEWSCALL (' + message + ') by: ' + str(chat_id) + ' at: ' + mtime + ' ' + mdate + '\n'
    with open('log', 'a') as f:
        f.write(text)
    f.close()
    bot.sendMessage(chat_id=chat_id, text=reply, reply_markup=reply_markup, parse_mode='HTML')


# This function handles the
# user requests and works
# off all queued jobs
def der_standard_handler(bot, update_id):
    for update in bot.getUpdates(offset=update_id, timeout=10):
        chat_id = update.message.chat_id
        update_id = update.update_id + 1
        message = update.message.text
        if chat_id == ADMIN_ID and '/admin' in message:
            admin.handler(bot, message, chat_id)
        elif '/start' in message:
            tele.unique_user(chat_id)
        elif '/subscribe' in message:
            tele.handle_subscriber(chat_id, 'a')
            bot.sendMessage(chat_id=chat_id, text='Registrierung Erfolgreich!')
        elif '/unsubscribe' in message:
            tele.handle_subscriber(chat_id, 'd')
            bot.sendMessage(chat_id=chat_id, text='Sie erhalten nun keine täglichen Nachrichten mehr!')
        elif '/news' in message:
            news = generate_news_message(message)
            admin.news_call()
            mtime = time.strftime('%X')[:5]
            mdate = time.strftime('%d.%m.%y')
            text = 'NEWSCALL (Basic) by: ' + str(chat_id) + ' at: ' + mtime + ' ' + mdate + '\n'
            with open('log', 'a') as f:
                f.write(text)
            f.close()

            bot.sendMessage(chat_id=chat_id, text=news, parse_mode='HTML')
        elif '/topic' in message:
            custom_keyboard = [['International'], ['Inland'], ['Wirtschaft'], ['Web'], ['Sport'],
                               ['Panorama'], ['Etat'], ['Kultur'], ['Wissenschaft'], ['Gesundheit'], ['Bildung'],
                               ['Reisen'], ['Lifestyle']]
            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            bot.sendMessage(chat_id=chat_id, text='Wählen Sie ihr gewünschtes Thema!', reply_markup=reply_markup)
        elif message == 'International':
            topic_handler(bot, message, chat_id)
        elif message == 'Inland':
            topic_handler(bot, message, chat_id)
        elif message == 'Wirtschaft':
            topic_handler(bot, message, chat_id)
        elif message == 'Web':
            topic_handler(bot, message, chat_id)
        elif message == 'Sport':
            topic_handler(bot, message, chat_id)
        elif message == 'Panorama':
            topic_handler(bot, message, chat_id)
        elif message == 'Etat':
            topic_handler(bot, message, chat_id)
        elif message == 'Kultur':
            topic_handler(bot, message, chat_id)
        elif message == 'Wissenschaft':
            topic_handler(bot, message, chat_id)
        elif message == 'Gesundheit':
            topic_handler(bot, message, chat_id)
        elif message == 'Bildung':
            topic_handler(bot, message, chat_id)
        elif message == 'Reisen':
            topic_handler(bot, message, chat_id)
        elif message == 'Lifestyle':
            topic_handler(bot, message, chat_id)
    return update_id
