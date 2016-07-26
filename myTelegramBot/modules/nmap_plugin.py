from argparse import ArgumentParser, ArgumentError

from nmap import PortScanner
from telegram.ext import CommandHandler
from telegram.ext.dispatcher import run_async

from myTelegramBot.PluginSystem import BasePlugin


class NmapPlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super(NmapPlugin, self).__init__(*args, **kwargs)

    @staticmethod
    def __check_for_idiot_friends(text):
        import string
        if text is None or len(text) <= 0:
            return False

        valid_chars = "-_.,%s%s" % (string.ascii_letters, string.digits)
        if len(''.join(c for c in text if c in valid_chars)) != len(text):
            return True
        return False

    @run_async
    def scan(self, bot, update, args):
        chat_id = update.message.chat_id
        from_user = update.message.from_user.username

        parser = ArgumentParser(prog='nmap_plugin')
        parser.add_argument('-host', required=True)
        parser.add_argument('-ports', required=False, default=None)
        parser.add_argument('-all', required=False, default=False, type=bool)
        parser.add_argument('-raw', required=False, default=None)
        try:
            p = parser.parse_args(args)
            for param in vars(p):
                if self.__check_for_idiot_friends(getattr(p, param)):
                    bot.sendMessage(
                        chat_id,
                        text='{} you are a funny guy... but go to try to be an h4x0r somewhere else.'.format(from_user)
                    )
                    if from_user == 'dzonerzy':
                        bot.sendMessage(chat_id,
                                        text='Amico del jaguaro... Ti fo un rutto ne `i viso che ti fo diventa` bello!'
                                        )
                    return
        except ArgumentError:
            bot.sendMessage(chat_id, text="Wrong parameters passed.")
            return

        arguments = '-sV'
        if p.all is True:
            arguments = '-A'

        bot.sendMessage(chat_id, text="Command accepted, running nmap against: {}".format(p.host))
        nm = PortScanner()
        nm.scan(hosts=p.host, ports=p.ports, arguments=arguments)

        msg = ''
        for host in nm.all_hosts():
            msg = '----------------------------------------------------\n'
            msg += 'Host: {} ({})\n'.format(host, nm[host].hostname())
            msg += 'State: {}\n'.format(nm[host].state())
            for proto in nm[host].all_protocols():
                msg += 'Protocol : {}\n'.format(proto)
                lport = nm[host][proto].keys()
                lport.sort()
                for port in lport:
                    msg += '\tport : {}\tstate : {}\n'.format(port, nm[host][proto][port]['state'])
        msg = 'Empty response object received.' if msg == '' else msg
        bot.sendMessage(chat_id, text=msg)

    def setup(self):
        self.dispatcher.add_handler(CommandHandler("scan", self.scan, pass_args=True))


def initialize(*args, **kwargs):
    return NmapPlugin(*args, **kwargs)
