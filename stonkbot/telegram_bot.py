from dbhelper import DBHelper
from api_keys import TELEGRAM_BOT_TOKEN

from telegram.ext import (
    Updater, 
    CommandHandler, 
    MessageHandler, 
    Filters,
    ConversationHandler
)

TICKER_ADD, TICKER_DELETE = range(2)

class TelegramBot:
    def __init__(self):
        self.db = DBHelper()
        self.db.setup()
        
        self.token = TELEGRAM_BOT_TOKEN
        
        self.updater = Updater(token=self.token)
        self.dispatcher = self.updater.dispatcher
        
        conv_handler = ConversationHandler(
            entry_points = [
                CommandHandler('start', self.start),
                CommandHandler('add', self.add_ticker_message),
                CommandHandler('delete', self.delete_ticker_message),
                CommandHandler('list', self.get_tickers)
            ],
            states = {
                TICKER_ADD: [
                    MessageHandler(Filters.text, self.add_ticker)
                ],
                TICKER_DELETE: [
                    MessageHandler(Filters.text, self.delete_ticker)
                ]
            },
            fallbacks = [MessageHandler(Filters.text('done'), self.done)]
        )
        
        self.dispatcher.add_handler(conv_handler)
        
        
    def start_bot(self):
        self.updater.start_polling()
        self.updater.idle()

    def stop_bot(self):
        self.updater.stop()

    def start(self, update, context) -> int:
        update.message.reply_text(
            'Input command.\n'
            'Add ticker: /add\n'
            'Delete ticker: /delete\n'
            'List tickers: /list\n'
        )
    
        return ConversationHandler.END

    def add_ticker_message(self, update, context) -> int:
        update.message.reply_text('Input ticker to add')
        return TICKER_ADD
    
    def add_ticker(self, update, context) -> int:
        self.db.add_ticker(owner=update.effective_chat.id, ticker=update.message.text)
        update.message.reply_text('Ticker added')
        return ConversationHandler.END
    
    def delete_ticker_message(self, update, context) -> int:
        update.message.reply_text('Input ticker to delete')
        return TICKER_DELETE
    
    def delete_ticker(self, update, context) -> int:
        self.db.delete_ticker(owner=update.effective_chat.id, ticker=update.message.text)
        update.message.reply_text('Ticker deleted')
        return ConversationHandler.END
    
    def get_tickers(self, update, context) -> int:
        tickers = self.db.get_tickers(update.effective_chat.id)
        
        parsedtickers = ''
        for i in tickers:
            parsedtickers += i
            parsedtickers += '\n'
        
        update.message.reply_text('Your tickers:\n' + parsedtickers)
        
        return ConversationHandler.END
    
    def done(update, context) -> int:
        return ConversationHandler.END