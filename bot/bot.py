import praw
import time
import pickle
import os
from bot.utils import *


__author__ = 'https://github.com/lebeli'
__copyright__ = 'Copyright 2019'
__license__ = 'MPL 2.0'
__version__ = '0.1.0'
__maintainer__ = 'https://github.com/lebeli'
__status__ = 'Dev'


class CriticAggregatorBot:
    SAVE_PATH = 'resources/submissions_save.pkl'

    def __init__(self):
        self.submissions = {}
        self.submissions_save = []

    def get_submissions(self):
        return self.submissions

    def new_submissions(self):
        if os.path.exists(CriticAggregatorBot.SAVE_PATH) and os.path.getsize(CriticAggregatorBot.SAVE_PATH):
            with open('resources/submissions_save.pkl', 'rb') as file:
                self.submissions_save = pickle.load(file)
        reddit = praw.Reddit('opencritic_bot')
        subreddit = reddit.subreddit('games')
        for submission in subreddit.search('review thread', time_filter='week'):
            if submission.id not in self.submissions_save:
                self.submissions[submission.id] = submission
        if self.submissions:
            return True
        return False

    def save_submissions(self, submissions):
        with open(CriticAggregatorBot.SAVE_PATH, 'wb') as file:
            pickle.dump(submissions, file, protocol=pickle.HIGHEST_PROTOCOL)

    def reply(self, aggregator='OpenCritic'):
        for k, v in self.submissions.copy().items():
            try:
                time.sleep(10)
                post_opencritic_scores(v, aggregator)
                del self.submissions[k]
            except praw.exceptions.APIException:
                raise praw.exceptions.APIException
            self.submissions_save.append(v.id)
        self.save_submissions(self.submissions_save)
        self.submissions = {}
