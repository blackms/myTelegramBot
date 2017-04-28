import base64
import datetime
import re
import smtplib
from collections import OrderedDict

from Crypto.Cipher import AES
from telegram.emoji import Emoji
from telegram.ext import MessageHandler, Filters, CommandHandler

import myTelegramBot.libs.gmail as gmail
from myTelegramBot.PluginSystem import BasePlugin
from myTelegramBot.core.config_manager import FileConfigObject


class MyFilter(Filters):
    def __init__(self):
        super(MyFilter, self).__init__()

    @staticmethod
    def text(message):
        return message.text if str(Emoji.FORK_AND_KNIFE) in message.text.encode('utf-8') else None


class Dish(object):
    def __init__(self, name, dish_type):
        self.name = name
        self.type = dish_type

    def __str__(self):
        return '{}'.format(self.name)


def check_user(method):
    def wrapped(self, *a, **ka):
        user = a[1].message.from_user.id
        chat_id = a[1].message.chat_id
        if user in [x.user_id for x in self.sm.get_user_session(user)]:
            return method(self, *a, **ka)
        else:
            a[0].sendMessage(chat_id, 'Sorry, you dont have enough privileges')
            return
    return wrapped


class LunchPlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        self.username = None
        self.password = None
        self.config = FileConfigObject()
        if 'sessions_manager' in kwargs.keys():
            self.sm = kwargs.pop('sessions_manager') or None
        super(LunchPlugin, self).__init__(*args, **kwargs)
        self.__secret_key = 'f9d5ccf180f948c107042433c29d8b6d'
        self.cipher = AES.new(self.__secret_key, AES.MODE_ECB)
        # Try to load config from file
        if self.config.get_section('lunch_plugin') is not None:
            username = self.config.get_option(section='lunch_plugin', key='username')
            password = self.config.get_option(section='lunch_plugin', key='password')
            if username is not None and password is not None:
                self.username = self.cipher.decrypt(base64.b64decode(username))
                self.password = self.cipher.decrypt(base64.b64decode(password))
        self.reservations = {}
        self.dishes = OrderedDict()
        self.last_update = None

    def _load_dishes(self, bot, chat_id):
        g = gmail.login(self.username, self.password)

        dishes = []
        for elem in g.inbox().mail(sender='sebast.pietro@libero.it', on=datetime.date.today()):
            elem.fetch()
            dishes = ''.join(elem.body.splitlines())
            self.last_update = elem.sent_at
        if len(dishes) <= 0:
            bot.sendMessage(chat_id, "Non ho ancora ricevuto la nuova mail del menu... Attendi Ciccione.")
            return False

        match_obj = re.search(r'PRIMI PIATTI:(.*)SECONDI PIATTI:(.*)PIATTI FREDDI:(.*)CONTORNI:(.*)DESSERT', dishes,
                              re.I)
        # Create local dictionary to map dishes and use them for reservations
        p_indexes = ['p', 's', 'f', 'c']
        p_num = 1
        for group in p_indexes:
            pos = 0
            for elem in [line for line in match_obj.group(p_num).split(";") if len(line) > 0]:
                self.dishes["{}{}".format(group, pos)] = elem
                pos += 1
            # Reset dish number
            p_num += 1
        return True

    def print_dishes(self, bot, update):
        chat_id = update.message.chat_id

        if self.username is None or self.password is None:
            bot.sendMessage(chat_id, "Prima devi dirmi su che mail guardare... Fava.")
            return

        if len(self.dishes) <= 0 or datetime.datetime.today().date() > self.last_update.date():
            if not self._load_dishes(bot, chat_id):
                return

        msg = "Menu` del: {}\n".format(self.last_update)
        msg += "Primi Piatti:\n{}".format(
            '\n'.join(
                [": ".join(x) for x in {k: v for k, v in self.dishes.items() if k.startswith('p')}.items()]
            )
        )
        msg += "\n\nSecondi Piatti:\n{}".format(
            '\n'.join(
                [": ".join(x) for x in {k: v for k, v in self.dishes.items() if k.startswith('s')}.items()]
            )
        )
        msg += "\n\nPiatti Freddi:\n{}".format(
            '\n'.join(
                [": ".join(x) for x in {k: v for k, v in self.dishes.items() if k.startswith('f')}.items()]
            )
        )
        msg += "\n\nContorni:\n{}".format(
            '\n'.join(
                [": ".join(x) for x in {k: v for k, v in self.dishes.items() if k.startswith('c')}.items()]
            )
        )
        bot.sendMessage(chat_id, msg)

    @check_user
    def set_credential(self, bot, update, args):
        chat_id = update.message.chat_id
        username = args[0]
        password = args[1]

        assert username is not None and password is not None, Exception("username and password cannot be None.")
        self.username = username
        self.password = password

        # Write config to file
        if self.config.get_section('lunch_plugin') is None:
            self.config.add_section('lunch_plugin')
        self.config.set_option('lunch_plugin', 'username', base64.b64encode(self.cipher.encrypt(username.rjust(32))))
        self.config.set_option('lunch_plugin', 'password', base64.b64encode(self.cipher.encrypt(password.rjust(32))))

        # Give to user the feedback
        bot.sendMessage(chat_id, "Credential Set.")

    def reserve(self, bot, update, args):
        """
        :type update: telegram.update.Update
        :param bot:
        :param update:
        :param args:
        :return:
        """
        chat_id = update.message.chat_id
        if len(update.message.from_user.username) <= 0:
            user = update.message.from_user.id
        else:
            user = update.message.from_user.username

        usage = 'Command Usage: /prenota [pN] [pN] [pN].'
        if len(args) <= 0:
            bot.sendMessage(chat_id, usage)
            return

        if len(self.dishes) <= 0:
            if self._load_dishes(bot, chat_id) is False:
                return

        reservation = []
        # Parse dishes from message
        for elem in args:
            # Validate each arg
            if elem not in self.dishes.keys():
                bot.sendMessage(chat_id, 'Non ho idea di cosa sia: {}... Riprova.'.format(elem))
                return
            reservation.append(self.dishes[elem])
        self.reservations[user] = reservation
        bot.sendMessage(chat_id, 'Ok: {}, hai prenotato:\n{}'.format(user, '\n'.join(self.reservations[user])))

    @check_user
    def send_mail(self, bot, update):
        chat_id = update.message.chat_id

        if len(self.reservations) <= 0:
            bot.sendMessage(chat_id, 'Non ci sono prenotazioni da inviare.')
            return

        msg = ""
        pos = 1
        # Build message
        for reservation in self.reservations.items():
            msg += "Persona n{}:\n{}\n\n".format(pos, "\n".join(reservation[1]))
            pos += 1

        bot.sendMessage(chat_id, 'Sto per prenotare:\n{}'.format(msg))

        server = 'smtp.gmail.com'
        port = 587

        session = smtplib.SMTP(server, port)
        session.set_debuglevel(False)
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(user=self.username, password=self.password)

        msg = "\r\n".join([
            "From: rocchi.b.a@gmail.com",
            "To: alessio.rocchi@staff.aruba.it",
            "CC: rocchi.b.a@gmail.com",
            "Subject: Prenotazione Aruba",
            "",
            "{}".format(msg)
        ])

        session.sendmail(from_addr=self.username, to_addrs=self.username, msg=msg)

    @check_user
    def recap(self, bot, update):
        chat_id = update.message.chat_id

        msg = ""
        if len(self.reservations.items()) <= 0:
            msg = "Non ci sono prenotazioni al momento."
            # Build message
        else:
            for reservation in self.reservations.items():
                msg += "{} ha preso:\n{}\n\n".format(reservation[0], "\n".join(reservation[1]))

        bot.sendMessage(chat_id, 'Prenotazione del: {}\n{}'.format(self.last_update, msg))

    def add_note(self, bot, update, args):
        chat_id = update.message.chat_id
        note = ' '.join(args)
        if len(update.message.from_user.username) <= 0:
            user = update.message.from_user.id
        else:
            user = update.message.from_user.username

        self.reservations[user].append('Note: {}'.format(note))
        bot.sendMessage(chat_id, 'Riepilogo prenotazione:\n{}'.format(
            '\n'.join(self.reservations[user])
        ))

    @check_user
    def purge_reservations(self, bot, update):
        chat_id = update.message.chat_id
        self.reservations = {}
        bot.sendMessage(chat_id, 'Prenotazioni rimosse.')

    def register_me(self, bot, update):
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id

    def unregister_me(self, bot, update):
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id

    def setup(self):
        self.dispatcher.add_handler(
            MessageHandler([MyFilter.text], self.print_dishes)
        )
        self.dispatcher.add_handler(
            CommandHandler('set_mail_login', self.set_credential, pass_args=True)
        )
        self.dispatcher.add_handler(
            CommandHandler('prenota', self.reserve, pass_args=True)
        )
        self.dispatcher.add_handler(
            CommandHandler('invia', self.send_mail, pass_args=False)
        )
        self.dispatcher.add_handler(
            CommandHandler('riepilogo', self.recap, pass_args=False)
        )

        self.dispatcher.add_handler(
            CommandHandler('nota', self.add_note, pass_args=True)
        )
        self.dispatcher.add_handler(
            CommandHandler('elimina_prenotazioni', self.purge_reservations, pass_args=False)
        )
        self.dispatcher.add_handler(
            CommandHandler('menu', self.print_dishes)
        )

        self.dispatcher.add_handler(
            CommandHandler('registrami', self.register_me, pass_args=False)
        )

        self.dispatcher.add_handler(
            CommandHandler('toglimi', self.unregister_me, pass_args=False)
        )


def initialize(*args, **kwargs):
    return LunchPlugin(*args, **kwargs)
