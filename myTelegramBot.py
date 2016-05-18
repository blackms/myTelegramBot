from myTelegramBot import MyTelegramBot
from argparse import ArgumentParser
import sys

if __name__ == '__main__':
    parser = ArgumentParser(prog='myTelegramBot')
    parser.add_argument('--token', help='Token to use.', required=True, dest='token')
    p = parser.parse_args()

    bot = MyTelegramBot(name="TestBot", token=p.token)
    bot.start_bot()





