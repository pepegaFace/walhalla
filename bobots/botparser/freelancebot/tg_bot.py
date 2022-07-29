import asyncio
import datetime
import json
import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold, hunderline, hcode, hlink
from aiogram.dispatcher.filters import Text
from aiogram import md
from config import token, user_id

from parserPython import Client

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands="start")
async def start(message: types.Message):
    start_buttons = ["freelance", "kwork"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer("Лента фриланса", reply_markup=keyboard)


async def get_all_news(site):
    start = datetime.time(10, 0, 0)
    end = datetime.time(18, 0, 0)
    while True:
        if start < datetime.datetime.now().time() < end:
            print(f'\nCORRECT TIME: {start < datetime.datetime.now().time() < end}\n')
            with open(site + '.json') as file:

                kwork_init_dict = json.load(file)
                have_something_to_send = False
                await bot.send_message(user_id, f'Поиск новых объявлений по {site}', disable_notification=True)
                for i, u in enumerate(kwork_init_dict[:5]):
                    if not kwork_init_dict[i]['send']:
                        have_something_to_send = True
                        kwork_init_dict[i]['send'] = True
                        # item_message = [u['url'], u['title'], u['article']]
                        item_message = [u['url'], u['article']]
                        await bot.send_message(user_id, item_message, disable_notification=True)
                    else:
                        item_message = f'Нет новых объявлений по {site}'

                if item_message == f'Нет новых объявлений по {site}' and not have_something_to_send:
                    await bot.send_message(user_id, f'{md.quote_html(item_message)}', disable_notification=True)

                if have_something_to_send:
                    with open(site + '.json', "w") as file:
                        json.dump(kwork_init_dict, file, indent=3, ensure_ascii=False)

                await asyncio.sleep(900)
        else:
            await asyncio.sleep(900)


@dp.message_handler(Text(equals="freelance"))
async def get_freelance(message: types.Message):
    with open("freelance.json") as file:
        dict = json.load(file)
        await message.answer('Последние 5 объявлений по freelance:')
        for i in dict[:5]:
            item_message = [i['url'], i['article']]
            await message.answer(f'{md.quote_html(item_message)}')


@dp.message_handler(Text(equals="kwork"))
async def get_freelance(message: types.Message):
    with open("kwork.json") as file:
        dict = json.load(file)
        print(f'\n\n\n dict lenght: {len(dict)}\n\n\n')
        await message.answer('Последние 5 объявлений по kwork:')
        for i in dict[:5]:
            item_message = [i['url'], i['article']]
            await message.answer(f'{md.quote_html(item_message)}')


if __name__ == '__main__':
    sites = ['freelance', 'kwork']

    freeloop = asyncio.get_event_loop()
    freeloop.create_task(get_all_news(site=sites[0]))

    kwloop = asyncio.get_event_loop()
    kwloop.create_task(get_all_news(site=sites[1]))

    executor.start_polling(dp)
