from telegram.ext import CommandHandler
from telegram.ext.dispatcher import run_async
from argparse import ArgumentParser
from nmap import PortScanner


@run_async
def scan(bot, update, args):
    chat_id = update.message.chat_id

    parser = ArgumentParser(prog='nmap_plugin')
    parser.add_argument('-host', required=True)
    parser.add_argument('-ports', required=False, default=None)
    parser.add_argument('-all', required=False, default=False, type=bool)
    parser.add_argument('-raw', required=False, default=None)
    p = parser.parse_args(args)

    arguments = '-sV'
    if p.all is True:
        arguments = '-A'

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
    bot.sendMessage(chat_id, text=msg)


def setup(dispatcher):
    dispatcher.addHandler(CommandHandler("scan", scan, pass_args=True))