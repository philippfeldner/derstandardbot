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
    if tele.time_trigger('06:00') or tele.time_trigger('08:00') or \
       tele.time_trigger('10:00') or tele.time_trigger('12:00') or \
       tele.time_trigger('14:00') or tele.time_trigger('16:00') or \
       tele.time_trigger('18:00') or tele.time_trigger('20:00'):
            tele.send_to_subscriber(bot, generate_news_message('/news'), time.strftime('%H%M'))


# Fetches the news using urllib.request
# returns a tuples of URLs and headlines
# Potentially gets stuck in loop when internet issues
def get_news(news, topic=''):
    re_url = ''
    re_title = ''
    link = ''
    if news == 'derstandard':
        link = 'http://text.derstandard.at' + '/' + topic
        re_url = r'</font></a><br><a href="(.*?)".*?<strong>.*?</strong>'
        re_title = r'</font></a><br><a href=".*?".*?<strong>(.*?)</strong>'

    while True:
        try:
            source = urllib.request.urlopen(link)
            break
        except urllib.error.URLError:
            if (int(time.strftime('%M')) % 5) == 0:
                print('Connectivity Issues')
            time.sleep(10)

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
    reply += '<b>Die aktuellen Schlagzeilen auf derstandard.at:</b> \n\n'
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
            source = urllib.request.urlopen('http://text.derstandard.at/' + message)
            break
        except urllib.error.URLError:
            if (int(time.strftime('%M')) % 5) == 0:
                print('Connectivity Issues')
            time.sleep(10)

    derstandard = source.read().decode('utf-8')
    regex = r'</font></a><br><a href="(.*?)".*?<strong>(.*?)</strong>'
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
        elif '/info' in message:
            reply = '<b>Liebe User!</b>\n\n' + 'Dieser Service basiert auf Python und läuft ' \
                    'auf einem Raspberry Pi. Ich kann somit also nicht für ständige Laufzeit garantieren!\n\n' + \
                    'Dies ist ein Einzel/Freizeitprojekt und Ich agiere vollkommen unabhängig von ' + \
                    '(c) derStandard.at!' + \
                    ' Ich habe <b>KEINE</b> Rechte auf jegliche Inhalte und verlinke lediglich!\n\n' + \
                    'Der Quellcode ist frei einsehbar auf:\n' + \
                    'https://github.com/philippfeldner/TelegramBots\n' + \
                    'Bei Fragen/Anregungen/Beschwerden/Bugreports:\n' + \
                    '<b>Telegram</b>: @PhilippFeldner\n' + \
                    '<b>Email</b>: feldnerphilipp@gmail.com'
            bot.sendMessage(chat_id=chat_id, text=reply, parse_mode='HTML', disable_web_page_preview=True)
        elif '/service' in message:
            time_keyboard = [['✅ 06:00', '❎ 06:00'], ['✅ 08:00', '❎ 08:00'],
                             ['✅ 10:00', '❎ 10:00'], ['✅ 12:00', '❎ 12:00'],
                             ['✅ 14:00', '❎ 14:00'], ['✅ 16:00', '❎ 16:00'],
                             ['✅ 18:00', '❎ 18:00'], ['✅ 20:00', '❎ 20:00'],
                             ['Fertig!']]
            reply_markup = telegram.ReplyKeyboardMarkup(time_keyboard)
            reply = 'Bitte wählen Sie ihre gewünschten Sendezeiten!\n' + \
                    'Auf Fertig! drücken um die Tastatur zu schließen!'
            bot.sendMessage(chat_id=chat_id, text=reply, reply_markup=reply_markup)
        elif '✅' in message:
            tele.handle_subscriber(chat_id, 'a', message)
        elif '❎' in message:
            tele.handle_subscriber(chat_id, 'd', message)
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
        elif message == 'Fertig!':
            reply_markup = telegram.ReplyKeyboardHide()
            reply = 'Ihre Einstellungen wurden übernommen!'
            bot.sendMessage(chat_id=chat_id, text=reply, reply_markup=reply_markup)
        elif '/thema' in message:
            custom_keyboard = [[telegram.Emoji.GLOBE_WITH_MERIDIANS + ' International'],
                               [telegram.Emoji.MOUNTAIN_CABLEWAY + ' Inland'],
                               [telegram.Emoji.FACTORY + ' Wirtschaft'], [telegram.Emoji.ALIEN_MONSTER + ' Web'],
                               [telegram.Emoji.SOCCER_BALL + ' Sport'], [telegram.Emoji.NEWSPAPER + ' Panorama'],
                               [telegram.Emoji.TELEVISION + ' Etat'], [telegram.Emoji.VIOLIN + ' Kultur'],
                               [telegram.Emoji.MICROSCOPE + ' Wissenschaft'], [telegram.Emoji.SYRINGE + ' Gesundheit'],
                               [telegram.Emoji.BOOKS + ' Bildung'], [telegram.Emoji.AIRPLANE + ' Reisen'],
                               [telegram.Emoji.TOP_HAT + ' Lifestyle'], [telegram.Emoji.FAMILY + ' Familie']]
            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            reply = 'Wählen Sie ihr gewünschtes Thema!'
            bot.sendMessage(chat_id=chat_id, text=reply, reply_markup=reply_markup)
        elif 'International' in message:
            topic_handler(bot, 'International', chat_id)
        elif 'Inland' in message:
            topic_handler(bot, 'Inland', chat_id)
        elif 'Wirtschaft' in message:
            topic_handler(bot, 'Wirtschaft', chat_id)
        elif 'Web' in message:
            topic_handler(bot, 'Web', chat_id)
        elif 'Sport' in message:
            topic_handler(bot, 'Sport', chat_id)
        elif 'Panorama' in message:
            topic_handler(bot, 'Panorama', chat_id)
        elif 'Etat' in message:
            topic_handler(bot, 'Etat', chat_id)
        elif 'Kultur' in message:
            topic_handler(bot, 'Kultur', chat_id)
        elif 'Wissenschaft' in message:
            topic_handler(bot, 'Wissenschaft', chat_id)
        elif 'Gesundheit' in message:
            topic_handler(bot, 'Gesundheit', chat_id)
        elif 'Bildung' in message:
            topic_handler(bot, 'Bildung', chat_id)
        elif 'Reisen' in message:
            topic_handler(bot, 'Reisen', chat_id)
        elif 'Lifestyle' in message:
            topic_handler(bot, 'Lifestyle', chat_id)
        elif 'Familie' in message:
            topic_handler(bot, 'Familie', chat_id)
    return update_id
