from myTelegramBot.modules.whois_plugin import whois_hndlr
from pluginbase import PluginBase
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import partial
import logging
import os

# Initialize plugin system
plugin_base = PluginBase(package='myTelegramBot.plugins')

# Enable logging functions
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

# For easier usage calculate the path relative to here.
here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)


class MyTelegramBot(object):
    """Represent the main application class"""

    def __init__(self, name, token=""):
        self.name = name
        self.token = token
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher

        # Load Plugins
        self.source = plugin_base.make_plugin_source(searchpath=[get_path('./modules')])
        self.__load_plugins()

        # Initialize main handlers
        self.dispatcher.addHandler(CommandHandler("start", self.start))
        self.dispatcher.addErrorHandler(self.error)

    def __load_plugins(self):
        for plugin in self.source.list_plugins():
            plugin = self.source.load_plugin(plugin)
            plugin.setup(self.dispatcher)

    @staticmethod
    def start(bot, update):
        """
        Function handler to answer start command
        :param bot: bot object
        :param update: update object
        """
        bot.sendMessage(update.message.chat_id, text='Hi!')

    @staticmethod
    def error(bot, update, error):
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def start_bot(self):
        self.updater.start_polling()
        self.updater.idle()

    def stop_bot(self):
        self.updater.stop()
