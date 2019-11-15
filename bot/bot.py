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
    SAVE_PATH = 'resources/submissions_save.pkl'

    def __init__(self):
        self.interval = 3600
        self.start_time = utc_time_now()
        self.submit = {}
        self.edit = {}
        self.submissions_save = {'submission_id': np.array([]), 'time': np.array([]),
                                 'comment_id': np.array([]), 'aggregator': np.array([])}
        self.reddit = praw.Reddit('opencritic_bot')
        self.subreddit = self.reddit.subreddit('games')
        if os.path.exists(CriticAggregatorBot.SAVE_PATH) and os.path.getsize(CriticAggregatorBot.SAVE_PATH):
            self.submissions_save = self.load_submissions()

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

    def get_submissions(self):
        return self.submit

    def new_submissions(self):
        for submission in self.subreddit.search('title:review thread', time_filter='day'):
            if submission.id not in self.submissions_save['submission_id']:
                self.submit[submission.id] = submission
        if self.submit:
            return True
        return False

    def save_submissions(self):
        with open(CriticAggregatorBot.SAVE_PATH, 'wb') as file:
            pickle.dump(self.submissions_save, file, protocol=pickle.HIGHEST_PROTOCOL)

    def load_submissions(self):
        with open(CriticAggregatorBot.SAVE_PATH, 'rb') as file:
            return pickle.load(file)

    def reply(self, aggregator='OpenCritic'):
        for id, submission in self.submit.copy().items():
            time.sleep(2)
            try:
                comment = submission.reply(get_reply_body(submission, aggregator) + get_reply_footer())
            except praw.exceptions.APIException:
                print("Exception!")
                continue
            self.submissions_save['comment_id'] = np.append(self.submissions_save['comment_id'], [comment.id])
            del self.submit[id]
            self.submissions_save['submission_id'] = np.append(self.submissions_save['submission_id'], [submission.id])
            self.submissions_save['time'] = np.append(self.submissions_save['time'], [datetime.now()])
            self.submissions_save['aggregator'] = np.append(self.submissions_save['aggregator'], [aggregator])
        self.save_submissions()
        self.submit = {}

    def update(self):
        for i, (sid, cid, agg) in enumerate(zip(self.submissions_save['submission_id'].copy(), self.submissions_save['comment_id'].copy(), self.submissions_save['aggregator'].copy())):
            comment = self.reddit.comment(cid)
            reply_body = get_reply_body(self.reddit.submission(sid), agg)
            try:
                if comment.author is None:
                    self.remove_save(i)
                    print('Comment was removed.')
                    continue
                if reply_body not in comment.body:
                    comment.edit(reply_body + get_reply_footer() + get_reply_edit_time(utc_time_now()))
                    print('Comment edited.')
                else:
                    print('No changes detected.')
            except praw.exceptions.ClientException:
                print('Comment not found.')
                continue

    def remove_save(self, idx):
        self.submissions_save['submission_id'] = np.delete(self.submissions_save['submission_id'], idx)
        self.submissions_save['comment_id'] = np.delete(self.submissions_save['comment_id'], idx)
        self.submissions_save['aggregator'] = np.delete(self.submissions_save['aggregator'], idx)
        self.submissions_save['time'] = np.delete(self.submissions_save['time'], idx)
        self.save_submissions()

    def recent_submissions(self):
        if len(self.submissions_save['submission_id']) == 0:
            return False
        keep_idx = [i for i, t in enumerate(self.submissions_save['time']) if (datetime.now() - t).days < 2]
        self.submissions_save['submission_id'] = self.submissions_save['submission_id'][keep_idx]
        self.submissions_save['time'] = self.submissions_save['time'][keep_idx]
        self.submissions_save['comment_id'] = self.submissions_save['comment_id'][keep_idx]
        self.submissions_save['aggregator'] = self.submissions_save['aggregator'][keep_idx]
        return True

    def load_all_comments(self):
        user_agent = self.reddit.user.me(use_cache=True)
        all_comments = user_agent.comments.new(limit=None)
        comments = [ac for ac in all_comments if get_reply_footer() in ac.body]
        self.submissions_save['submission_id'] = np.array([c.parent_id.split('_')[1] for c in comments])
        self.submissions_save['time'] = np.array([utc_time_now() for c in comments])
        self.submissions_save['comment_id'] = np.array([c.id for c in comments])
        self.submissions_save['aggregator'] = np.array(['OpenCritic' for i in range(len(comments))])
        print('')
