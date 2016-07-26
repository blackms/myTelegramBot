import logging
import os
from functools import partial

from pluginbase import PluginBase
from telegram.ext import Updater, CommandHandler

from myTelegramBot.core.sessions import SessionManager, Session
from myTelegramBot.core.auth_manager import *

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

        # Initialize core Manager
        self._session_manager = SessionManager(name='myTelegramBotSessionManager')

        # Load Plugins
        self.source = plugin_base.make_plugin_source(searchpath=[get_path('./modules')])
        self.__load_plugins()

        # Initialize main handlers
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_error_handler(self.error)

    def __load_plugins(self):
        for plugin in self.source.list_plugins():
            base = self.source.load_plugin(plugin)
            plugin = base.initialize(dispatcher=self.dispatcher, sessions_manager=self._session_manager)
            # Add Handler to Telegram Command
            plugin.setup()

    def login(self, bot, update, args):
        """
        Callback method for login command.
        :param bot:
        :param update:
        :param args:
        :type bot: telegram.bot.Bot
        :type update: telegram.update.Update
        :type args: list
        :return:
        """
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id
        u, p = args[0], args[1]
        auth_file = '{}/stuff/auth.ini'.format(os.getcwd())
        auth_method = Md5hashFile(file_path=auth_file)
        if auth_method.exists(u):
            if not auth_method.compare_password(user=u, clear_text_password=p):
                bot.sendMessage(chat_id, 'Password mismatch. Sorry.')
                return
        else:
            bot.sendMessage(chat_id, 'Username not found. Sorry.')
            return
        # User is valid, map to correct permission object
        user_obj = auth_method.user_dict[u]
        if user_obj['level'] == '1':
            obj = NormalUser(username=u, user_id=user_id)
        elif user_obj['level'] == '2':
            obj = PowerUser(username=u, user_id=user_id)
        elif user_obj['level'] == '3':
            obj = AdminUser(username=u, user_id=user_id)
        else:
            raise UserNotFound('User with name: {} not found.'.format(u))
        _session = Session(user=obj)
        # Register new session into session manager
        bot.sendMessage(chat_id, 'Registered user: {} to session: {}'.format(u, _session.id))
        self._session_manager.add_user_session(_session)

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
        self.dispatcher.add_handler(
            CommandHandler(command='login', callback=self.login, pass_args=True)
        )
        self.updater.start_polling()
        self.updater.idle()

    def stop_bot(self):
        self.updater.stop()
