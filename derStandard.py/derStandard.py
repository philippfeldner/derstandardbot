###########################################################
# derStandard.at - News service bot
# ---------------------------------
# author: Philipp Feldner
# contact: feldnerphilipp@gmail.com
# github: github.com/PhilippFeldner
#
# Made possible by the Python Telegram API:
# https://github.com/eternnoir/pyTelegramBotAPI
#
# I do not claim any content! Source: http://derstandard.at
###########################################################

import telegram
import time

from urllib.error import URLError
from telelib import tele
from telelib import admin
from telelib import news


# This function creates the bot
# and runs in an infinite loop
# waiting for jobs to be done
def der_standard():
    bot = telegram.Bot(tele.get_bot_token('derstandard.token'))
    try:
        update_id = bot.getUpdates()[0].update_id
    except IndexError:
        update_id = None
    while True:
        try:
            news.sub_service(bot)
            update_id = news.der_standard_handler(bot, update_id)
        except telegram.TelegramError as e:
            if e.message in ("Bad Gateway", "Timed out"):
                time.sleep(2)
            elif e.message == "Unauthorized":
                update_id += 1
            else:
                raise e
        except URLError:
            time.sleep(2)


########################################
# WHERE EVERYTHING BEGINS
########################################
admin.session_start('set')
der_standard()


