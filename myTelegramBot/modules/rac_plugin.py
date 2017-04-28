from __future__ import print_function

import os

from telegram.ext import MessageHandler, Filters, CommandHandler

from textblob import TextBlob

from myTelegramBot.PluginSystem import BasePlugin

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage
from oauth2client import tools

import datetime


class CalendarManager(object):
    def __init__(self):
        self.Scopes = 'https://www.googleapis.com/auth/calendar'
        self.ClientSecretFile = 'client_secret.json'
        self.ApplicationName = 'Google Calendar API Python Quickstart'
        self.credentials = self._get_credentials()

    def _get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'calendar-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.ClientSecretFile, self.Scopes)
            flow.user_agent = self.ApplicationName
            credentials = tools.run(flow, store)
        return credentials

    def get_events(self):
        http = self.credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='ha1i5mboaknnd8jos469thnjuk@group.calendar.google.com', timeMin=now, maxResults=10,
            singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events


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

        cal_manager = CalendarManager()
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
