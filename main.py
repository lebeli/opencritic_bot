from bot.bot import CriticAggregatorBot
from exceptions.server import InternalServerError


__author__ = 'https://github.com/lebeli'
__copyright__ = 'Copyright 2019'
__license__ = 'MPL 2.0'
__version__ = '0.1.0'
__maintainer__ = 'https://github.com/lebeli'
__status__ = 'Dev'


if __name__ == '__main__':
    criticAggregatorBot = CriticAggregatorBot()
    if criticAggregatorBot.recent_comments():
        print('Checking for updates.')
        try:
            criticAggregatorBot.update(aggregator='OpenCritic')
        except InternalServerError:
            print('Could not reach server.')
    if criticAggregatorBot.new_submissions():
        print('New submissions!')
        criticAggregatorBot.reply(aggregator='OpenCritic')
    else:
        print('No submissions found.')
