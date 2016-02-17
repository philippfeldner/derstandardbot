import re
import time
from telelib import tele

SESSION_START = 'not set'
SEND_TIME_1 = '08:00'
SEND_TIME_2 = '13:00'


# calling this function without parameters
# increases newscall in the newscall plaintext file
# calling it with get simply returns the value
def news_call(arg='inc'):
    if arg == 'inc':
        with open('newscall', 'r') as f:
            value = f.read()
        f.close()
        value = int(value)
        value += 1
        with open('newscall', 'w') as f:
            f.write(str(value))
    elif 'get':
        with open('newscall', 'r') as f:
            value = f.read()
        f.close()
        return value


# Calling this functin without
# parameters returns the start time
# calling with set resets start time
def session_start(arg='get'):
    global SESSION_START
    if arg == 'get':
        return SESSION_START
    elif arg == 'set':
        mtime = time.strftime('%X')[:5]
        mdate = time.strftime('%d/%m/%y')
        SESSION_START = mtime + ' ' + mdate
        print(SESSION_START)


# This function checks
# if the time_val parameter
# is actually a valid time
def valid_time(time_v):
    hours = int(time_v[:2])
    minutes = int(time_v[3:])
    if 0 <= hours < 24 and 0 <= minutes < 59:
        return True
    else:
        return False


# This function simply returns
# the amount of unique users stored
# in the users plaintext file
def user_count():
    with open('user', 'r') as f:
        user = f.read()
    f.close()
    return user.count('\n')


# This function simply returns
# the amount of subscribers stored
# in the subscriber plain text file
def sub_count():
    with open('subscriber', 'r') as f:
        subscriber = f.read()
    f.close()
    return subscriber.count('\n')


# This function returns
# the value of the 2
# autonews sending times
def send_time(val):
    global SEND_TIME_1
    global SEND_TIME_2
    if val == 1:
        return SEND_TIME_1
    if val == 2:
        return SEND_TIME_2


# This function lets you
# set the two times of
# autonews val is 1 or 2
def set_time(time_v, val):
    global SEND_TIME_1
    global SEND_TIME_2
    if val == '1':
        SEND_TIME_1 = time_v
    elif val == '2':
        SEND_TIME_2 = time_v


# This function handles all
# the admin commands which
# can only be called by the admin
def handler(bot, message, chat_id):
    paramater = message.split()
    re_time = r'\d\d:\d\d'
    re_num = r'\d'

    if 'settime' in message:
        if len(paramater) != 4:
            bot.sendMessage(chat_id=chat_id, text='Invalid parameter count!')
            return
        num = re.findall(re_num, paramater[2])
        time_v = re.findall(re_time, paramater[3])
        if num is not None and time_v is not None:
            if valid_time(time_v[0]) and (int(num[0]) == 1 or int(num[0]) == 2):
                set_time(time_v[0], num[0])
                bot.sendMessage(chat_id=chat_id, text='Sucess!')
            else:
                bot.sendMessage(chat_id=chat_id, text='Input invalid!')
                return

    elif 'userinfo' in message:
        user = user_count()
        subscriber = sub_count()
        reply = 'Total amount of ' + str(user) + ' unique users and ' + str(subscriber) + ' subscribers.\n' + \
                str(int((subscriber / user) * 100)) + '% of all users are subscribed!\n' \
                '---------------------------------\n' \
                'Total amount of Newscalls: ' + news_call('get') + '\n' \
                'Autonews (1): ' + SEND_TIME_1 + '\n' + \
                'Autonews (2): ' + SEND_TIME_2 + '\n'

        bot.sendMessage(chat_id=chat_id, text=reply)

    elif 'running' in message:
        reply = 'Running since: ' + session_start()
        bot.sendMessage(chat_id=chat_id, text=reply)
    elif 'log' in message:
        with open('log', 'rb') as doc:
            bot.sendDocument(chat_id=chat_id, document=doc, filename='log.txt')
        doc.close()

    elif 'broadcast' in message:
        if tele.broadcast(bot, message):
            bot.sendMessage(chat_id=chat_id, text='Broadcast Sucessfull')
        else:
            bot.sendMessage(chat_id=chat_id, text='Did you use []?')

    else:
        default = 'Available admin commands: \n' + \
                  'Format: /admin [command] [param] \n' + \
                  '-------------------------------------\n' \
                  'settime [1 or 2] [HH:MM] - automessage service \n' + \
                  'running - returns uptime \n' + \
                  'userinfo - returns some statistics\n' + \
                  'log - sends you the current logfile\n' \
                  'broadcast [] - sends the message within [] to everybody!'
        bot.sendMessage(chat_id=chat_id, text=default)
