import praw
import pickle
import os
import time

from datetime import datetime
from utils.parsing import *
from utils.reply import *
from utils.time import utc_time_now


__author__ = 'https://github.com/lebeli'
__copyright__ = 'Copyright 2019'
__license__ = 'MPL 2.0'
__version__ = '0.1.0'
__maintainer__ = 'https://github.com/lebeli'
__status__ = 'Dev'


class CriticAggregatorBot:
    def __init__(self):
        self.interval = 3600
        self.start_time = utc_time_now()
        self.reddit = praw.Reddit('opencritic_bot')
        self.subreddit = self.reddit.subreddit('games')
        self.comments = []
        self.submissions = []
        self.load_recent_comments()
        self.load_new_submissions()

    def run(self):
        while True:
            # increase interval every 5h to max. 1h
            if (self.start_time - utc_time_now()).seconds >= 18000 and self.interval < 3600:
                self.interval = self.interval + 900
            if self.recent_submissions():
                print('Checking for updates.')
                self.update()
            if self.new_submissions():
                self.interval = 900
                print('New submissions!')
                self.reply(aggregator='MetaCritic')
            else:
                print('No submissions found.')
            time.sleep(self.interval)

    def reply(self, aggregator='OpenCritic'):
        for sub in self.submissions:
            try:
                sub.reply(get_reply_body(sub, aggregator) + get_reply_footer())
            except praw.exceptions.APIException:
                print("Exception!")
                continue
        self.submissions = []

    def update(self, aggregator='OpenCritic'):
        recent_submissions = [self.reddit.submission(c.parent_id.split('_')[1]) for c in self.comments]
        for sub, comm in zip(recent_submissions, self.comments):
            reply_body = get_reply_body(sub, aggregator)
            try:
                if reply_body not in comm.body:
                    comm.edit(reply_body + get_reply_footer() + get_reply_edit_time(utc_time_now()))
                    print('Comment edited.')
                else:
                    print('No changes detected.')
            except praw.exceptions.ClientException:
                print('Comment not found.')
                continue

    def load_new_submissions(self):
        comment_ids = [c.parent_id.split('_')[1] for c in self.comments]
        self.submissions = [sub for sub in self.subreddit.search('title:review thread', time_filter='day')
                            if sub.id not in comment_ids]

    def new_submissions(self):
        return not len(self.submissions) == 0

    def load_all_comments(self):
        user_agent = self.reddit.user.me(use_cache=True)
        all_comments = user_agent.comments.new(limit=None)
        self.comments = [ac for ac in all_comments if get_reply_footer() in ac.body]

    def load_recent_comments(self):
        user_agent = self.reddit.user.me(use_cache=True)
        all_weekly_comments = [awc for awc in user_agent.comments.top('week')]
        self.comments = [awc for awc in all_weekly_comments if get_reply_footer() in awc.body]

    def recent_comments(self):
        return not len(self.comments) == 0
