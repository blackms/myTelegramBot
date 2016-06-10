import whois
from telegram.ext import CommandHandler


class WhoisPlugin(object):
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    @staticmethod
    def whois_handler(bot, update, args):
        chat_id = update.message.chat_id
        domain = args[0] if len(args) > 0 else None

        whois_response = whois.whois(domain) if whois.whois(domain) else None
        if whois_response is None:
            bot.sendMessage(chat_id, text="Sorry, I can't retrieve whois information about: {}.".format(domain))
            return
        bot.sendMessage(chat_id, text='Whois: {}'.format(whois_response.text))

    def setup(self):
        self.dispatcher.add_handler(CommandHandler("whois", self.whois_handler, pass_args=True))


def initialize(dispatcher):
    return WhoisPlugin(dispatcher)
