import whois
from telegram.ext import CommandHandler


def whois_hndlr(bot, update, args):
    chat_id = update.message.chat_id
    domain = ""
    if len(args) > 0:
        domain = args[0]
    else:
        bot.sendMessage(chat_id, text="Specify the domain or the IP to search.")

    w = whois.whois(domain)
    if len(w.text) == 0:
        bot.sendMessage(chat_id, text="Sorry, I can't retrieve whois information about: {}.".format(domain))
        return
    bot.sendMessage(chat_id, text='Whois: {}'.format(w.text))


def setup(dispatcher):
    dispatcher.addHandler(CommandHandler("whois", whois_hndlr, pass_args=True))