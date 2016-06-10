import re

from telegram.emoji import Emoji
from telegram.ext import MessageHandler, Filters, CommandHandler

import myTelegramBot.libs.gmail as gmail
from myTelegramBot.PluginSystem import BasePlugin


class MyFilter(Filters):
    def __init__(self):
        super(MyFilter, self).__init__()

    @staticmethod
    def text(message):
        return message.text if str(Emoji.FORK_AND_KNIFE) in message.text.encode('utf-8') else None


class LunchPlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        self.username = None
        self.password = None
        super(LunchPlugin, self).__init__(*args, **kwargs)
    
    def print_dishes(self, bot, update):
        chat_id = update.message.chat_id

        if self.username is None or self.password is None:
            bot.sendMessage(chat_id, "Prima devi dirmi su che mail guardare... Fava.")
            return
        
        g = gmail.login(self.username, self.password)

        for elem in g.inbox().mail(unread=True, sender='sebast.pietro@libero.it'):
            elem.fetch()
            dishes = ''.join(elem.body.splitlines())

        match_obj = re.search(r'PRIMI PIATTI:(.*)SECONDI PIATTI:(.*)CONTORNI:(.*)DESSERT', dishes, re.I)
        msg = "Primi:\n{}\n\nSecondi:\n{}\n\nContorni:\n{}\n".format(
            '\n'.join([line for line in match_obj.group(1).split(";") if len(line) > 0]),
            '\n'.join([line for line in match_obj.group(2).split(";") if len(line) > 0]),
            '\n'.join([line for line in match_obj.group(3).split(";") if len(line) > 0]),
        )
        
        bot.sendMessage(chat_id, msg)

    def set_credential(self, bot, update, args):
        chat_id = update.message.chat_id
        username = args[0]
        password = args[1]

        assert username is not None and password is not None, Exception("username and password cannot be None.")
        self.username = username
        self.password = password
        bot.sendMessage(chat_id, "Credential Set.")

    def setup(self):
        self.dispatcher.add_handler(
            MessageHandler([MyFilter.text], self.print_dishes),
            )
        self.dispatcher.add_handler(
            CommandHandler('set_mail_login', self.set_credential, pass_args=True)
        )


def initialize(dispatcher):
    return LunchPlugin(dispatcher)
