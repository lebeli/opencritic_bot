from bot.bot import CriticAggregatorBot
import praw
import time


__author__ = 'https://github.com/lebeli'
__copyright__ = 'Copyright 2019'
__license__ = 'MPL 2.0'
__version__ = '0.1.0'
__maintainer__ = 'https://github.com/lebeli'
__status__ = 'Dev'


if __name__ == '__main__':
    criticAggregatorBot = CriticAggregatorBot()
    print(int(9.5))
    while True:
        if criticAggregatorBot.new_submissions():
            print("New submissions!")
            try:
                criticAggregatorBot.reply(aggregator='MetaCritic')
            except praw.exceptions.APIException:
                print("Waiting...")
                time.sleep(600)
                continue
        else:
            print("No updates found.")
        time.sleep(1800)
