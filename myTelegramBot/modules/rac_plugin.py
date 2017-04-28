from __future__ import print_function

from telegram.ext import MessageHandler, Filters
from textblob import TextBlob

from myTelegramBot.PluginSystem import BasePlugin


class HelloFilter(Filters):
    def __init__(self):
        super(HelloFilter, self).__init__()

    @staticmethod
    def text(message):
        blob = TextBlob(message.text)
        if 'ciao' in blob.tokens.lower() and 'racbot' in blob.tokens.lower():
            return message.text
        return None


class EventsFilter(Filters):
    def __init__(self):
        super(EventsFilter, self).__init__()

    @staticmethod
    def text(message):
        blob = TextBlob(message.text)
        if 'eventi' in blob.tokens.lower():
            return message.text
        return None


class RacPlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super(RacPlugin, self).__init__(*args, **kwargs)

    @staticmethod
    def hello(bot, update, user_data):
        """
        :type bot: telegram.bot.Bot
        :type update: telegram.update.Update
        :type args: list
        :return:
        """
        chat_id = update.message.chat_id
        user = update.message.from_user

        bot.sendMessage(chat_id, "Ciao: {}!".format(user.first_name))

    @staticmethod
    def show_events(bot, update, user_data):
        chat_id = update.message.chat_id
        user = update.message.from_user

        cal_manager = GoogleCalendar()
        events = cal_manager.get_events()
        bot.sendMessage(chat_id, "Certo {}, ecco i prossimi 10 eventi secondo il calendario:".format(user.first_name))
        for event in events:
            ev = event['start'].get('dateTime', event['start'].get('date'))
            bot.sendMessage(chat_id, "{} - {}".format(ev, event['summary']))

    def setup(self):
        self.dispatcher.add_handler(
            MessageHandler([HelloFilter.text], self.hello, pass_user_data=True)
        )
        self.dispatcher.add_handler(
            MessageHandler([EventsFilter.text], self.show_events, pass_user_data=True)
        )


def initialize(*args, **kwargs):
    return RacPlugin(*args, **kwargs)
