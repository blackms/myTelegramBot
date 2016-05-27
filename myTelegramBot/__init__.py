from pluginbase import PluginBase
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from functools import partial
from session import SessionManager
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
        self.authenticator = None

        # Initialize session Manager
        self.__session_manager = SessionManager(name='myTelegramBotSessionManager')

        # Load Plugins
        self.source = plugin_base.make_plugin_source(searchpath=[get_path('./modules')])
        self.__load_plugins()

        # Initialize main handlers
        self.dispatcher.addHandler(CommandHandler("start", self.start))
        self.dispatcher.addErrorHandler(self.error)

    def __load_plugins(self):
        for plugin in self.source.list_plugins():
            base = self.source.load_plugin(plugin)
            plugin = base.initialize(self.dispatcher)
            # Add Handler to Telegram Command
            plugin.setup()

    def set_auth_method(self, *args, **kwargs):
        auth = kwargs.pop('auth_method')
        self.authenticator = auth(*args, **kwargs)

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
