import os

from telegram.ext import MessageHandler, Filters, CommandHandler

from myTelegramBot.PluginSystem import BasePlugin


class MoinePlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        self.words_file = '{}/stuff/words.txt'.format(os.getcwd())
        self.words = {}
        with open(self.words_file, 'r') as fh:
            self.words = {k: v for k, v in map(lambda x: x.split(':'), fh.readlines())}
        super(MoinePlugin, self).__init__(*args, **kwargs)
    
    def moinize(self, bot, update, args):
        """
        :type bot: telegram.bot.Bot
        :type update: telegram.update.Update
        :type args: list
        :return:
        """
        chat_id = update.message.chat_id
        word_to_find = args[0] if len(args) > 0 else None
        if word_to_find is None:
            bot.sendMessage(chat_id, 'Dimmi cosa vuoi sapere... Non sono [ancora] indovino...')
            return
        if word_to_find not in self.words.keys():
            bot.sendMessage(chat_id, 'Mi spiace, non ho tale vocabolo in memoria, sentiti libero di aggiugerlo.')
            return
        bot.sendMessage(chat_id, self.words[word_to_find])

    def add_word(self, bot, update, args):
        """
        :type bot: telegram.bot.Bot
        :type update: telegram.update.Update
        :type args: list
        :return:
        """
        chat_id = update.message.chat_id
        word_to_add = args[0] if len(args) > 0 else None
        if word_to_add is None:
            bot.sendMessage(chat_id, 'Non fare il furbo Jack...')
            return
        with open(self.words_file, 'w+') as fh:
            fh.write(word_to_add)
        msg = "Ok man! Aggiunta la word!"
        bot.sendMessage(chat_id, msg)

    def remove_word(self, bot, update, args):
        """
        :type bot: telegram.bot.Bot
        :type update: telegram.update.Update
        :type args: list
        :return:
        """
        chat_id = update.message.chat_id
        word_to_remove = args[0] if len(args) > 0 else None
        if word_to_remove is None:
            bot.sendMessage(chat_id, 'Non ho questa parola in memoria...')
            return
        new_dict = self.words.pop(word_to_remove, None)
        with open(self.words_file, 'w') as fh:
            fh.write("\n".join(new_dict.items()))
        self.words = new_dict
        msg = 'Word rimossa. Needs satisfied.'
        bot.sendMessage(chat_id, msg)

    def setup(self):
        self.dispatcher.add_handler(CommandHandler("moinize", self.moinize, pass_args=True))
        self.dispatcher.add_handler(CommandHandler("add_word", self.add_word, pass_args=True))
        self.dispatcher.add_handler(CommandHandler("remove_word", self.remove_word, pass_args=True))


def initialize(*args, **kwargs):
    return MoinePlugin(*args, **kwargs)
