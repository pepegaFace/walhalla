import math
import re
import time
import pandas as pd
from sqlalchemy import create_engine
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageToDeleteNotFound
from config import token, user_id


bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# Коннект к БД pars_db
engine = create_engine('postgresql+psycopg2://root')

status = 'False'

database_content = pd.read_sql_table('admpars_train', con=engine)


table_to_write = 'admpars_sample_1'

if engine.has_table(table_to_write):
    sample_data = pd.read_sql_table(table_to_write, con=engine)
    ARTICLE_COUNTER = len(sample_data)
else:
    ARTICLE_COUNTER = 0

database_content['status'] = status


# Инициализация кнопок под вывода под сообщением
inline_btn_good = InlineKeyboardButton('Хорошо', callback_data='goodBtn')
inline_btn_bad = InlineKeyboardButton('Плохо', callback_data='badBtn')
inline_kb = InlineKeyboardMarkup().add(inline_btn_good, inline_btn_bad)

# Счетчик сообщений
msg_counter = 0


def add_to_db(article_id, article_status):
    """
    Функция, отвечающая за добавление новости в БД
    :param article_id: идентификатор новости
    :param article_status: статус, который нужно установить для новости, при записи в БД
    """

    database_content["status"][article_id] = article_status

    print(f"Article with url: {database_content['url'][article_id]}, "
          f"with status: {database_content['status'][article_id]} "
          f"and id:{article_id}")

    # Подготовка данных для перевода в датафрейм
    data = {'id': database_content["id"][article_id],
            'url': database_content["url"][article_id],
            'title': " ".join(database_content["title"][article_id].split()),
            'article': " ".join(database_content["article"][article_id].split()),
            'city': database_content["city"][article_id],
            'tag': database_content["tag"][article_id],
            'status': database_content["status"][article_id]}

    df = pd.DataFrame(data=data, index=[article_id])

    # Добавление датафрейма в таблицу sample_1
    df.to_sql(table_to_write, con=engine, if_exists='append', index=False)

    # print('\n\n\n\n ================================================================================================='
    #       '===============================================================================')
    # print(df)
    # some_content = pd.read_sql_table(table_to_write, con=engine)
    # print(f'\n{some_content}')
    # print('=========================================================================================================='
    #       '===================================================================== \n\n\n\n ')


async def delete_messages(interval_start, interval_end, chat_id):
    """
    Функция, отвечающая за удаление сообщений из чата
    :param interval_start: id первого сообщения
    :param interval_end: id последнего сообщения
    :param chat_id: id чата, из которого удаляются сообщения
    """

    global ARTICLE_COUNTER

    for message_index in reversed(range(interval_start, interval_end)):
        try:
            # print(f'Message index for deletion: {message_index}...')
            await bot.delete_message(chat_id=chat_id, message_id=message_index)
        except MessageToDeleteNotFound:
            print(f'Message with id {message_index} does not exist')


async def show_article(article_id):
    """
       Функция, отвечающая за вывод заголовка и записи новости в телеграме
       :param article_id: идентификатор новости
       """

    # Вызов глобальных счетчиков
    global ARTICLE_COUNTER
    global msg_counter
    msg_counter = 0
    if " ".join(database_content["article"][article_id].split()) != '':

        # Очищение тектса и заголовка новости от лишних пробелов
        article = " ".join(database_content["article"][article_id].split())
        article = re.sub('[*_<>]', '', article)
        # print(article)

        await bot.send_message(user_id, f'Новость номер {ARTICLE_COUNTER}')
        msg_counter += 1

        # Проверка на длину текста для вывода, если текст больше лимита в 4096, то делим сообщение на сегменты
        # и шлем его по частям
        if len(article) > 4096:
            rounded_value = math.ceil(len(article) / 4096)
            counter = 0
            for x in range(0, len(article), 4096):
                counter += 1
                # print(counter, rounded_value)
                if counter != rounded_value:
                    await bot.send_message(user_id, f'{article[x:x + 4096]}')
                    msg_counter += 1
                else:
                    await bot.send_message(user_id, f'{article[x:x + 4096]}',
                                           reply_markup=inline_kb)
                    msg_counter += 1

        else:
            await bot.send_message(user_id, article, reply_markup=inline_kb)
            msg_counter += 1
    else:
        # Если текст у новости отсуствует, то добавляем запись в БД со статусом False, и выводим следующую новость
        add_to_db(ARTICLE_COUNTER, 'False')
        ARTICLE_COUNTER += 1
        await show_article(ARTICLE_COUNTER)


@dp.message_handler(commands="start")
async def start(message: types.Message):
    global msg_counter

    msg_counter = 0

    start_buttons = ["Показать следующую новость."]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer("Лента новостей из БД", reply_markup=keyboard)


@dp.message_handler(Text(equals="Показать следующую новость."))
async def get_db(message: types.Message):
    global msg_counter

    await delete_messages(message.message_id - msg_counter,
                          message.message_id + 1,
                          user_id)

    await show_article(ARTICLE_COUNTER)


@dp.callback_query_handler(lambda c: c.data == 'goodBtn')
async def process_callback_btn_good(callback_query: types.CallbackQuery):
    """
    Функция, срабатывающая по нажатии кнопки 'Хорошо'
    добавляет запись в таблицу со статусом 'True'
    """
    global ARTICLE_COUNTER
    global msg_counter

    # await bot.answer_callback_query(callback_query.id)
    await delete_messages(callback_query.message.message_id - msg_counter + 1,
                          callback_query.message.message_id + 1,
                          callback_query.from_user.id)

    add_to_db(ARTICLE_COUNTER, 'True')
    ARTICLE_COUNTER += 1
    await show_article(article_id=ARTICLE_COUNTER)


@dp.callback_query_handler(lambda c: c.data == 'badBtn')
async def process_callback_btn_bad(callback_query: types.CallbackQuery):
    """
    Функция, срабатывающая по нажатии кнопки 'Плохо'
    добавляет запись в таблицу со статусом 'False'
    """
    global ARTICLE_COUNTER
    global msg_counter

    # await bot.answer_callback_query(callback_query.id)
    await delete_messages(callback_query.message.message_id - msg_counter + 1,
                          callback_query.message.message_id + 1,
                          callback_query.from_user.id)

    add_to_db(ARTICLE_COUNTER, 'False')
    ARTICLE_COUNTER += 1
    await show_article(article_id=ARTICLE_COUNTER)


if __name__ == '__main__':
    executor.start_polling(dp)
