"""
Базовый бот для отправки сообщения в редакционный чят.
Версия 0.000001 найтли.

После запуска забирает ячейку из дашборда в гугл-листах и отправляет её в чат редакции.
Предполагается на постановку на ежесуточный автозапуск.

"""

from telegram.bot import Bot
from secrets import tg_token, chat_id
from reporting_to_google_sheets import Reporting
import datetime
import random


# CREDENTIALS TO SERVICE ACC
CREDSTOSERVICE = 'credentials.json'


buzz = ('мужчина', 'парниша', 'любовник', 'редактор', 'гномик')
adjectives = ('полный', 'современный', 'самостоятельный', 'знатный', 'полноценный')
adverbs = ('знатно', 'всеобъемлюще', 'последовательно', 'значимо', 'серьезно')
verbs = ('улучшающий работу БТ', 'характеризующий эту конфу', 'влияющий на нас', 'влюбленный в себя')


def sample(l, n = 1):
    result = random.sample(l, n)
    if n == 1:
        return result[0]
    return result


def generate_buzz():
    buzz_terms = sample(buzz, 1)
    phrase = ' '.join([sample(adjectives), buzz_terms, sample(adverbs),
        sample(verbs)])
    return phrase.title()


def today_metric():
    if datetime.datetime.today().weekday() == 0:
        range_name = 'Dashboard!I42:I42'
        text_to_send = "На сегодня лучшим сотрудником KFC 'У Бугурт-Палыча' является: "
        # print("Monday")
    elif datetime.datetime.today().weekday() == 1:
        range_name = 'Dashboard!I46:I46'
        text_to_send = "Собрал больше всего переходов в паблик в расчете на один пост: "
        # print("Tuesday")
    elif datetime.datetime.today().weekday() == 2:
        range_name = 'Dashboard!Q42:Q42'
        text_to_send = "Выдумщик недели: "
        # print("Wednesday")
    elif datetime.datetime.today().weekday() == 2:
        range_name = 'Dashboard!Q46:Q46'
        text_to_send = "Самый виральный пост в расчете на минуту нахождения на стене: "
        # print("Tuesday")
    elif datetime.datetime.today().weekday() == 2:
        range_name = 'Dashboard!I42:I42'
        text_to_send = "Привел больше всего переходов в паблик: "
        # print("Friday")
    else:
        pass

    return range_name, text_to_send


if __name__ == '__main__':
    r = Reporting()
    service2 = r.auth()
    range_name, text_to_send = today_metric()
    editor_name = r.get_values(r, service2, range_name)
    phrase_of_day = generate_buzz().lower()
    text_to_bot = (
                    f"{text_to_send}{editor_name[0][0]}.\n{editor_name[0][0]}, ты сегодня "
                    f"{phrase_of_day}"
                )

    Bot(token=tg_token).send_message(chat_id=chat_id, text=text_to_bot)
