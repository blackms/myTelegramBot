from myTelegramBot import MyTelegramBot
from argparse import ArgumentParser
import logging
from daemonize import Daemonize

pid = "/tmp/test.pid"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
fh = logging.FileHandler("/var/log/myTelegramBot.log", "w")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
keep_fds = [fh.stream.fileno()]

token = ''


def main():
    logger.debug("Initializing main app...")
    bot = MyTelegramBot(name="TestBot", token=token)
    bot.start_bot()

if __name__ == '__main__':
    parser = ArgumentParser(prog='myTelegramBot')
    parser.add_argument('--token', help='Token to use.', required=True, dest='token')
    parser.add_argument('--daemon', help='Launch in daemon mode.', action='store_true')
    p = parser.parse_args()
    token = p.token

    if p.daemon:
        daemon = Daemonize(app="myTelegramBot", pid=pid, action=main, keep_fds=keep_fds)
        daemon.start()
    else:
        main()
