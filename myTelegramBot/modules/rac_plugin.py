from __future__ import print_function

import telegram
from telegram.ext import MessageHandler, Filters
from textblob import TextBlob

from myTelegramBot.PluginSystem import BasePlugin
from myTelegramBot.libs.gcal import GoogleCalendar

import datetime


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
        if 'eventi' in blob.tokens.lower() and 'racbot' in blob.tokens.lower():
            return message.text
        return None


class RacPlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super(RacPlugin, self).__init__(*args, **kwargs)

    @staticmethod
    def hello(bot, update):
        """
        Method which answer to an Hello
        :param bot:
        :type bot:
        :param update:
        :type update:
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
        msg = str()
        for event in events:
            try:
                start_time = datetime.datetime.strptime(event['start'].get('dateTime').split('+')[0],
                                                        '%Y-%m-%dT%H:%M:%S').__str__()
            except AttributeError:
                start_time = datetime.datetime.strptime(event['start'].get('date'), '%Y-%m-%d')
            if 'location' in event.keys():
                location = event['location']
            else:
                location = 'Mi dispiace, qualche pigro non ha inserito la location.'
            msg += "{} : {}. Luogo: {}\n\n".format(start_time, event['summary'], location)
        bot.sendMessage(chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

    def setup(self):
        self.dispatcher.add_handler(
            MessageHandler([HelloFilter.text], self.hello, pass_user_data=False)
        )
        self.dispatcher.add_handler(
            MessageHandler([EventsFilter.text], self.show_events, pass_user_data=True)
        )


def initialize(*args, **kwargs):
    return RacPlugin(*args, **kwargs)
