from bot.bot import CriticAggregatorBot
import praw
import time
import os


__author__ = 'https://github.com/lebeli'
__copyright__ = 'Copyright 2019'
__license__ = 'MPL 2.0'
__version__ = '0.1.0'
__maintainer__ = 'https://github.com/lebeli'
__status__ = 'Dev'


if __name__ == '__main__':
    criticAggregatorBot = CriticAggregatorBot()
    # if criticAggregatorBot.new_updates():
    #     print('New updates!')
    #     criticAggregatorBot.edit()
    if criticAggregatorBot.new_submissions():
        print('New submissions!')
        criticAggregatorBot.reply(aggregator='MetaCritic')
    else:
        print("No updates found.")

