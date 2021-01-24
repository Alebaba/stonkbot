from threading import Thread
import schedule
import time

from dbhelper import DBHelper
from api_keys import TELEGRAM_BOT_TOKEN
from telegram.ext import (
    Updater, 
    CommandHandler
)

class TelegramBot:
    def __init__(self):
        self.db = DBHelper()
        self.db.setup()
        
        self.token = TELEGRAM_BOT_TOKEN
        
        self.updater = Updater(token=self.token)
        self.dispatcher = self.updater.dispatcher     
        
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('add', self.add_ticker))
        self.dispatcher.add_handler(CommandHandler('delete', self.delete_ticker))
        self.dispatcher.add_handler(CommandHandler('list', self.get_tickers))
        
    def start_bot(self) -> None:
        self.updater.start_polling()
        self.updater.idle()
        
        schedule.every(15).minutes.do(self.check_technical_indicators)
        Scheduler.start()

    def start(self, update, context) -> None:
        update.message.reply_text(
            'Commands:\n'
            'Add ticker: /add <ticker>\n'
            'Delete ticker: /delete <ticker>\n'
            'List tickers: /list\n'
        )
    
    def add_ticker(self, update, context) -> None:
        self.db.add_ticker(owner=update.effective_chat.id, ticker=context.args[0])
        update.message.reply_text('Ticker added')
    
    def delete_ticker(self, update, context) -> None:
        self.db.delete_ticker(owner=update.effective_chat.id, ticker=context.args[0])
        update.message.reply_text('Ticker deleted')
    
    def get_tickers(self, update, context) -> None:
        tickers = self.db.get_tickers(update.effective_chat.id)
        
        parsedtickers = ''
        for i in tickers:
            parsedtickers += i
            parsedtickers += '\n'
        
        update.message.reply_text('Your tickers:\n' + parsedtickers)
    
    def check_technical_indicators(self):
        print("Testing check technicals timer")
        return

    def send_notification_message(self, owner, ticker, message):
        return

class Scheduler(Thread):
    @classmethod
    def start(cls):
        while True:
            schedule.run_pending()
            time.sleep(1)
