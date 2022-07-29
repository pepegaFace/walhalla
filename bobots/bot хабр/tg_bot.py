import asyncio
import datetime
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold, hunderline, hcode, hlink
from aiogram.dispatcher.filters import Text
from config import token, user_id

from parserPython import Client

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands="start")
async def start(message: types.Message):
    start_buttons = ["Python+нейрон", "laravel+верстка", "kwork+нейрон", "kwork+laravel"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer("Лента фриланса", reply_markup=keyboard)



@dp.message_handler(Text(equals="kwork+нейрон"))
async def get_kworkp(message: types.Message):
    with open("kworkp_data.json") as file:
        news_dicts = json.load(file)
        for k in sorted(news_dicts[:5]):
            

            await message.answer(k)


async def get_all_kworkp():
   while True:
        with open("kworkp_data.json") as file:
            news_dict4 = json.load(file)
            for n in sorted(news_dict4[:1]):

                await bot.send_message(user_id, n, disable_notification=True)

            await asyncio.sleep(1400)



@dp.message_handler(Text(equals="kwork+laravel"))
async def get_kwork(message: types.Message):
    with open("kwork_data.json") as file:
        news_dicts = json.load(file)
        for k in sorted(news_dicts[:5]):
            

            await message.answer(k)


async def get_all_kwork():
   while True:
        with open("kwork_data.json") as file:
            news_dict4 = json.load(file)
            for n in sorted(news_dict4[:1]):

                await bot.send_message(user_id, n, disable_notification=True)

            await asyncio.sleep(1300)

@dp.message_handler(Text(equals="Python+нейрон"))
async def get_python(message: types.Message):
    with open("data.json") as file:
        news_dicts = json.load(file)
        for i in sorted(news_dicts[:5]):
            

            await message.answer(i)



async def get_all_python():
   while True:
        with open("data.json") as file:
            news_dict3 = json.load(file)
            for n in sorted(news_dict3[:1]):

                await bot.send_message(user_id, n, disable_notification=True)

            await asyncio.sleep(1600)


@dp.message_handler(Text(equals="laravel+верстка"))
async def get_lara(message: types.Message):
    with open("data1.json") as file:
        news_dicts1 = json.load(file)
        for u in sorted(news_dicts1[ :5]):

            await message.answer(u)


async def get_all_news():
   while True:
        with open("data1.json") as file:
            news_dict2 = json.load(file)
            for n in sorted(news_dict2[:1]):

                await bot.send_message(user_id, n, disable_notification=True)

            await asyncio.sleep(1500)



if __name__ == '__main__':
    
    kwloop = asyncio.get_event_loop()
    kwloop.create_task(get_all_kworkp())

    deloop = asyncio.get_event_loop()
    deloop.create_task(get_all_python())

    keloop = asyncio.get_event_loop()
    keloop.create_task(get_all_kwork())

    loop = asyncio.get_event_loop()
    loop.create_task(get_all_news())
    executor.start_polling(dp)
