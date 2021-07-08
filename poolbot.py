#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""

Сам бот тут:
https://t.me/JustQuizBot


Source of example:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/pollbot.py

More datails:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/persistentconversationbot.py

https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/pollbot.py
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/pollbot.py
https://github.com/python-telegram-bot/python-telegram-bot/blob/92ff6a8e2bf77dc4225875b54f89af04fe61109d/tests/test_keyboardbutton.py
https://github.com/python-telegram-bot/python-telegram-bot/tree/master/telegram

Basic example for a bot that works with polls. Only 3 people are allowed to interact with each
poll/quiz the bot generates. The preview command generates a closed poll/quiz, exactly like the
one the user sends the bot

"""

import logging

from telegram import (
    Poll,
    ParseMode,
    KeyboardButton,
    KeyboardButtonPollType,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    PollAnswerHandler,
    PollHandler,
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


FIRST_LEVEL, SECOND_LEVEL, THIRD_LEVEL, FORTH_LEVEL, FIFTH_LEVEL, PREEND_LEVEL, END_LEVEL = range(7)

reply_keyboard = [['Поехали!']]
markup = ReplyKeyboardMarkup(reply_keyboard, force_reply=True, one_time_keyboard=False)

reply_keyboard_2 = [['Едем дальше']]
markup_2 = ReplyKeyboardMarkup(reply_keyboard_2, force_reply=True, one_time_keyboard=False)

reply_keyboard_3 = [['Я все понял!']]
markup_3 = ReplyKeyboardMarkup(reply_keyboard_3, force_reply=True, one_time_keyboard=False)


def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask user for input."""
    update.message.reply_text(
        "- Привет, я бот! Спасибо что пришел!\n"
        "Давай пройдем небольшой тест? ",
        reply_markup=markup,
    )
    return FIRST_LEVEL


def quiz(update: Update, context: CallbackContext) -> None:
    """Send a predefined poll"""
    questions = ["Ворона и лисица", "Лиса и виноград", "Колобок", "Кот и Лиса"]
    message = update.effective_message.reply_poll(
        "В какой из этих басен и сказок лисице не удалось достичь желаемого?",
        questions,
        type=Poll.QUIZ,
        correct_option_id=1,
        explanation="Давай сделаем вид, что мы этого не заметили!"
    )
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {
        message.poll.id: {"chat_id": update.effective_chat.id,
                          "message_id": message.message_id,
                          "quiz_num": 1,
                          "message_text": message.text,
                          "mess_poss": message.poll}
    }

    update.message.reply_text("Когда ответишь - не забудь нажать 'Едем дальше' или просто напиши 'Дальше' с клавиатуры",
                              reply_markup=markup_2)
    return SECOND_LEVEL


def quiz2(update: Update, context: CallbackContext) -> None:
    questions = ["Осла", "Козла", "Петуха", "Кота"]
    message = update.effective_message.reply_poll(
        "Какого из этих животных не было среди Бременских музыкантов?",
        questions,
        type=Poll.QUIZ,
        correct_option_id=1,
        explanation="Давай сделаем вид, что мы этого не заметили!"
    )
    return THIRD_LEVEL

def quiz3(update: Update, context: CallbackContext) -> None:
    questions = ["Лебедь", "Креветка", "Щука", "Рак"]
    message = update.effective_message.reply_poll(
        "Какой персонаж не вошел в знаменитую тройку Крылова?",
        questions,
        type=Poll.QUIZ,
        correct_option_id=1,
        explanation="Давай сделаем вид, что мы этого не заметили!"
    )
    return FORTH_LEVEL


def quiz4(update: Update, context: CallbackContext) -> None:
    questions = ["Горшок", "Воздушный шар", "Мед", "Хвост"]
    message = update.effective_message.reply_poll(
        "Какой подарок ко дню рождения Сова подарила ослику Иа?",
        questions,
        type=Poll.QUIZ,
        correct_option_id=3,
        explanation="Давай сделаем вид, что мы этого не заметили!"
    )
    return FIFTH_LEVEL


def quiz5(update: Update, context: CallbackContext) -> None:
    questions = ["Дверь", "Золотой ключик", "Котелок", "Сверчок"]
    message = update.effective_message.reply_poll(
        "Что было нарисовано на холсте в коморке Папы Карло?",
        questions,
        type=Poll.QUIZ,
        correct_option_id=2,
        explanation="Давай сделаем вид, что мы этого не заметили!"
    )
    return PREEND_LEVEL


def preend(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("ДА ТЫ ЭРУДИТ ЕБАН БОБАН! КРАСАВА, ЧЕМПИОН! \n\n"
                              "Посмотри на свой результат: \n"
                              "Если 0/5 — ты Андрей\n" 
                              "Если 1/5 — ты Алый гвозьд\n"
                              "Если 2/5 — ты Теплый квас\n"
                              "Если 3/5 — ты Знатный дровосек\n"
                              "Если 4/5 — ты Беспринципная седовласка\n"
                              "Если 5/5 — ты Сочный гематоген",
                              reply_markup=markup_3)
    return END_LEVEL


def theend(update: Update, context: CallbackContext) -> None:
    # context.bot.sendPhoto(chat_id=chat_id, photo="url_of_image", caption="This is the test photo caption")
    update.message.reply_text("А вот и все!\n"
                              "Cоветуем почитать классическую литературу, бро)\n"
                              "Вот тебе пару книжечек:\n"
                              "<a href='https://cloud.mail.ru/public/dCEi/CReTnzFBH'>Первая</a>\n"
                              "<a href='https://cloud.mail.ru/public/C3Gi/UmQGLPKtx'>Вторая</a>",parse_mode=ParseMode.HTML,
                              reply_markup=None,

                              )


def end(update: Update, context: CallbackContext) -> int:
    """End conversation from InlineKeyboardButton."""
    update.callback_query.answer()
    text = 'See you around!'
    update.callback_query.edit_message_text(text=text)
    return END


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN_HERE")
    dispatcher = updater.dispatcher

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST_LEVEL: [
                MessageHandler(Filters.regex('^(Поехали!)$'), quiz),
            ],
            SECOND_LEVEL: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), quiz2
                ),
            ],
            THIRD_LEVEL: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), quiz3
                ),
            ],
            FORTH_LEVEL: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), quiz4
                ),
            ],
            FIFTH_LEVEL: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), quiz5
                ),
            ],
            PREEND_LEVEL: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), preend
                ),
            ],
            END_LEVEL: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), theend
                ),
            ],

        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), end)],
        name="my_conversation"
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()