import os
import telebot

API_KEY = os.environ['API_KEY']

bot = telebot.TeleBot(API_KEY)
@bot.message_handler(commands=['Greet']) 

def greet(message):
  bot.reply_to(message, "Hey, how is it going")

bot.polling()