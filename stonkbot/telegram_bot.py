from threading import Thread
import schedule
import time

from stock_analysis import TechnicalAnalysis
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
        
        self.ta = TechnicalAnalysis()
        
        self.updater = Updater(token=TELEGRAM_BOT_TOKEN)
        self.dispatcher = self.updater.dispatcher         
        
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('add', self.add_ticker))
        self.dispatcher.add_handler(CommandHandler('delete', self.delete_ticker))
        self.dispatcher.add_handler(CommandHandler('list', self.list_tickers))
        self.dispatcher.add_handler(CommandHandler('check', self.check_technical_analysis_data)) # For testing only?
        
    def start_bot(self) -> None:
        self.updater.start_polling()
        self.updater.idle()
        
        schedule.every(15).minutes.do(self.check_technical_analysis_data)
        Scheduler.start()

    def start(self, update, context) -> None:
        update.message.reply_text(
            'Commands:\n'
            'Add ticker: /add <ticker>\n'
            'Delete ticker: /delete <ticker>\n'
            'List tickers: /list\n'
        )
    
    # TODO: add check if ticker exists
    def add_ticker(self, update, context) -> None:
        try:
            self.db.add_ticker(owner=update.effective_chat.id, ticker=context.args[0])
            update.message.reply_text('Ticker added')
        except IndexError:
            update.message.reply_text('Ticker name missing')
    
    def delete_ticker(self, update, context) -> None:
        try:
            self.db.delete_ticker(owner=update.effective_chat.id, ticker=context.args[0])
            update.message.reply_text('Ticker deleted')
        except IndexError:
            update.message.reply_text('Ticker name missing')
    
    def list_tickers(self, update, context) -> None:
        tickers = self.db.get_tickers(owner=update.effective_chat.id)
        
        parsedtickers = ''
        for i in tickers:
            parsedtickers += i
            parsedtickers += '\n'
        
        update.message.reply_text('Your tickers:\n' + parsedtickers)
    
    # TODO: Implement adjustable scheduling. (Use forcerefresh for that?)
    def check_technical_analysis_data(self, update, context) -> None:
        self.ta.update_date()
        owners = self.db.get_owners()
        for i in owners:
            message = ''
            tickers = self.db.get_tickers(owner=i)
            for j in tickers:
                #print(i + ' ' + j)
                self.ta.get_price_data(ticker=j, timeframe='daily')
                self.ta.get_technical_indicators(ticker=j)
                self.ta.get_bollinger_band_data(ticker=j)
                self.ta.get_rsi_data(ticker=j)
                
                bbiscrossed, bbexplanation = self.ta.bollinger_band_crossed(ticker=j, date=self.ta.currentdate)
                rsi = self.ta.rsi_limit_crossed(ticker=j, date=self.ta.currentdate)
                
                message += 'Ticker: ' + j + '\n'
                if bbiscrossed:
                    message += bbexplanation + '\n'
                if rsi > 70 or rsi < 30:
                    message += 'RSI: ' + str(rsi) + '\n'
                
                # TODO: improve API call usage system
                time.sleep(60)
            
            context.bot.send_message(chat_id=i, text=message)

class Scheduler(Thread):
    @classmethod
    def start(cls):
        while True:
            schedule.run_pending()
            time.sleep(1)
