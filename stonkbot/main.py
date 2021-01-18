from telegram_bot import TelegramBot

def main():
    telegramtokenfile = open('telegram_bot_token', 'r')
    bottoken = telegramtokenfile.readline()
    telegramtokenfile.close()
    
    alphavantageapikeyfile = open('alpha_vantage_api_keys', 'r')
    apikeys = alphavantageapikeyfile.readline()
    alphavantageapikeyfile.close()
    
    bot = TelegramBot(token=bottoken)
    bot.start_bot()

main()