import sys
import os
from telegram_bot import TelegramBot

def main():
    telegramtokenfile = open('telegram_bot_token', 'r')
    bottoken = telegramtokenfile.readline()
    telegramtokenfile.close()
    
    bot = TelegramBot(token=bottoken)
    bot.start_bot()

main()