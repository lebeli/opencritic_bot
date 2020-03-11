import praw
import time

from utils.reply import *
from utils.time import utc_time_now, get_time_from_s


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
                sub.reply(get_reply_body(sub, aggregator) + get_reply_footer() + get_reply_edit_time(utc_time_now()))
            except praw.exceptions.APIException:
                print("Exception!")
                continue
        self.submissions = []

    def update(self, aggregator='OpenCritic'):
        recent_submissions = [self.reddit.submission(c.parent_id.split('_')[1]) for c in self.comments]
        for sub, comment in zip(recent_submissions, self.comments):
            comment_time = get_time_from_s(comment.created_utc)
            current_time = utc_time_now()
            # consider only comments from last 7 days
            if (current_time - comment_time).days > 7:
                break
            reply_body = get_reply_body(sub, aggregator)
            try:
                if reply_body not in comment.body:
                    comment.edit(reply_body + get_reply_footer() + get_reply_edit_time(utc_time_now()))
                    print('Comment edited.')
                else:
                    print('No changes detected.')
            except praw.exceptions.ClientException:
                print('Comment not found.')
                continue

    def load_new_submissions(self):
        comment_ids = [c.parent_id.split('_')[1] for c in self.comments]
        self.submissions = [sub for sub in self.subreddit.search('title:review thread', time_filter='day')
                            if sub.id not in comment_ids and 'reddit.com' in sub.url]
        delete_idx = []
        # check if search results indeed review threads
        for sub in self.submissions:
            # cross-posted
            if sub.selftext_html is None:
                if 'opencritic' not in sub.crosspost_parent_list[0]['selftext']:
                    delete_idx.append(sub)
                continue
            # self post
            if 'opencritic' not in sub.selftext:
                delete_idx.append(sub)
        if delete_idx:
            for d in delete_idx:
                del(self.submissions[self.submissions.index(d)])



    def new_submissions(self):
        return not len(self.submissions) == 0

    def load_all_comments(self):
        user_agent = self.reddit.user.me(use_cache=True)
        all_comments = user_agent.comments.new(limit=None)
        self.comments = [ac for ac in all_comments if get_reply_footer() in ac.body]

    def load_recent_comments(self):
        user_agent = self.reddit.user.me(use_cache=True)
        all_new_comments = [anc for anc in user_agent.comments.new()]
        self.comments = [anc for anc in all_new_comments if "review spread at a glance" in anc.body]

    def recent_comments(self):
        return not len(self.comments) == 0
