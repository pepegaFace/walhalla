import telebot
import requests
from telebot import types

bot = telebot.TeleBot('1965012116:AAFBz6ltr3I6W5z8RzJEcywSmxH16FeL6Tk')
doc = open('/home/vadim/Рабочий стол/botHabr/test.csv', 'rb')

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Привет")
    keyboard = types.InlineKeyboardMarkup()
    five_k = types.InlineKeyboardButton(text='Python', callback_data='python')
    six_k = types.InlineKeyboardButton(text='phpLaravel', callback_data='phpLaravel')
    seven_k = types.InlineKeyboardButton(text='Фронтенд', callback_data='Javascrip')

    keyboard.add(five_k, six_k, seven_k)
    bot.send_message(message.chat.id, 'Выбери стек', reply_markup=keyboard)



bot.polling()

