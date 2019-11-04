import praw
import time
from datetime import datetime
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
        self.submit = {}
        self.update = {}
        self.submissions_save = {'submission_id': np.array([]), 'time': np.array([]),
                                 'comment_id': np.array([]), 'aggregator': np.array([])}
        self.reddit = praw.Reddit('opencritic_bot')
        self.subreddit = self.reddit.subreddit('games')
        if os.path.exists(CriticAggregatorBot.SAVE_PATH) and os.path.getsize(CriticAggregatorBot.SAVE_PATH):
            with open('resources/submissions_save.pkl', 'rb') as file:
                self.submissions_save = pickle.load(file)

    def get_submissions(self):
        return self.submit

    def new_submissions(self):
        for submission in self.subreddit.search('review thread', time_filter='week'):
            if submission.id not in self.submissions_save['submission_id']:
                self.submit[submission.id] = submission
        if self.submit:
            return True
        return False

    def save_submissions(self, submissions):
        with open(CriticAggregatorBot.SAVE_PATH, 'wb') as file:
            pickle.dump(submissions, file, protocol=pickle.HIGHEST_PROTOCOL)

    def reply(self, aggregator='OpenCritic'):
        for id, submission in self.submit.copy().items():
            try:
                time.sleep(2)
                reply_body = generate_reply_body(submission, aggregator)
                try:
                    comment = submission.reply(reply_body)
                except praw.exceptions.APIException:
                    print("Exception!")
                    continue
                self.submissions_save['comment_id'] = np.append(self.submissions_save['comment_id'], [comment.id])
                del self.submit[id]
            except praw.exceptions.APIException:
                raise praw.exceptions.APIException
            self.submissions_save['submission_id'] = np.append(self.submissions_save['submission_id'], [submission.id])
            self.submissions_save['time'] = np.append(self.submissions_save['time'], [datetime.now()])
            self.submissions_save['aggregator'] = np.append(self.submissions_save['aggregator'], [aggregator])
        self.save_submissions(self.submissions_save)
        self.submit = {}


    def edit(self):
        for sid, cid, agg in zip(self.submissions_save['submission_id'], self.submissions_save['comment_id'], self.submissions_save['aggregator']):
            time.sleep(2)
            reply_body = generate_reply_body(self.reddit.submission(sid), agg)
            #self.reddit.comment(cid).edit(reply_body)  # TODO: check if body has changed


    def new_updates(self):
        if len(self.submissions_save['submission_id']) == 0:
            return False
        keep_idx = [i for i, t in enumerate(self.submissions_save['time']) if ((t - datetime.now()).seconds / 3600) < 48]
        self.submissions_save['submission_id'] = self.submissions_save['submission_id'][keep_idx]
        self.submissions_save['time'] = self.submissions_save['submission_id'][keep_idx]
        self.submissions_save['comment_id'] = self.submissions_save['submission_id'][keep_idx]
        self.submissions_save['aggregator'] = self.submissions_save['aggregator'][keep_idx]
        return True
