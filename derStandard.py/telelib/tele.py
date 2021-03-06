import re
import time
from telegram import TelegramError
TIME_LOCK = False


# returns boolean if value
# matches the current time
# time format: HH:MM
def time_trigger(value):
    global TIME_LOCK
    unlock = ['01', '02', '03', '04', '05']
    if value == time.strftime('%H:%M') and not TIME_LOCK:
        TIME_LOCK = True
        return True
    elif time.strftime('%M') in unlock and TIME_LOCK:
        TIME_LOCK = False
        return False
    else:
        return False


# Due to having this publicly available I store my tokens
# in name.token. This function simply returns
# the token fitting the botname.
def get_bot_token(name):
    try:
        key = open(name).read()
    except IOError as e:
        raise e
    return key


# Every user has an unique ID
# in the Telegram API
# At bot /start they get added to the users file
def unique_user(chat_id):
    with open('user', 'r') as f:
        user = f.read()
    f.close()
    if not (str(chat_id) + '\n') in user:
        with open('user', 'w') as f:
            user += str(chat_id) + '\n'
            f.write(user)
            print('#############################################')
            print('New User: ' + str(chat_id) + ' is using the service!')
            print('Currently ' + str(user.count('\n')) + ' unique Users!')
            print('#############################################')
        f.close()


# This function either adds or removes
# a user from the list of subscribers
# saved in the subscriber file.
def handle_subscriber(chat_id, action, sub_t):
    regex = r'.*(\d\d:\d\d).*'
    sub_f = re.findall(regex, sub_t)
    if sub_f is not None and str(sub_f[0]) in ('06:00', '08:00', '10:00', '12:00',
                                               '14:00', '16:00', '18:00', '20:00'):
        sub_t = str(sub_f[0]).replace(':', '')
    file = 'subscriber/sub_' + sub_t
    with open(file, 'r') as f:
        subscriber = f.read()
    f.close()
    with open(file, 'w') as f:
        if action == 'a' and not (str(chat_id) + '\n' in subscriber):
            subscriber += str(chat_id) + '\n'
            f.write(subscriber)
            print('---------------------------------------------')
            print('User: ' + str(chat_id) + ' subscribed to this service!')
            print('---------------------------------------------')
        elif action == 'd' and str(chat_id) + '\n' in subscriber:
            subscriber = subscriber.replace(str(chat_id) + '\n', '')
            f.write(subscriber)
            print('---------------------------------------------')
            print('User: ' + str(chat_id) + ' unsubscribed from this service!')
            print('---------------------------------------------')
        else:
            f.write(subscriber)
    f.close()


# sends a news headlines to all subscribers!
# subscribers are stored in the
# subscriber plain text file
def send_to_subscriber(bot, news, sub_t):
    file = 'subscriber/sub_' + sub_t
    with open(file) as f:
        subscriber = f.readlines()
    for i in range(len(subscriber)):
        try:
            chat_id = int(subscriber[i])
            bot.sendMessage(chat_id=chat_id, text=news, parse_mode='HTML')
        except TelegramError as e:
            if e.message == 'Unauthorized':
                rm_t = sub_t[:2] + ':' + sub_t[2:]
                handle_subscriber(subscriber[i], 'd', rm_t)
                pass
            elif e.message == 'Bad request: chat not found':
                rm_t = sub_t[:2] + ':' + sub_t[2:]
                handle_subscriber(subscriber[i], 'd', rm_t)
                error = 'User: ' + subscriber[i] + 'deleted (Bad request!) in: ' + file
                print('---------------------------------------------')
                print(error)
                print('---------------------------------------------')
                with open('error_log', 'a') as f:
                    f.write(error)
                f.close()
                pass
            else:
                error = 'User: ' + subscriber[i] + 'causing: ' + e.message
                print('---------------------------------------------')
                print(error)
                print('---------------------------------------------')
                with open('error_log', 'a') as f:
                    f.write(error)
                f.close()
                pass
    print('---------------------------------------------')
    print(time.strftime('%H:%M'))
    print('Successfully send to all subscribers!')
    print('---------------------------------------------')


# Sends a broadcast message
# to every user that is
# listed in the user file
def broadcast(bot, message):
    regex = r'<(.*?)>'
    text = re.findall(regex, message, re.DOTALL)
    if not text:
        return False
    with open('user') as f:
        user = f.readlines()
    for i in range(len(user)):
        try:
            chat_id = int(user[i])
            bot.sendMessage(chat_id=chat_id, text=str(text[0]), parse_mode='HTML')
        except TelegramError as e:
            if e.message == 'Unauthorized':
                pass
            elif e.message == 'Bad request: chat not found':
                pass
            else:
                pass
    print('---------------------------------------------')
    print(time.strftime('%H:%M'))
    print('Broadcast: [' + str(text[0]) + '] send to everybody!')
    print('---------------------------------------------')
    return True
