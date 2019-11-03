import requests
from bs4 import BeautifulSoup
import numpy as np


__author__ = 'https://github.com/lebeli'
__copyright__ = 'Copyright 2019'
__license__ = 'MPL 2.0'
__version__ = '0.1.0'
__maintainer__ = 'https://github.com/lebeli'
__status__ = 'Dev'


def get_url_from_selftext(selftext, aggregator):
    url_path = selftext.split("{}.com/game/".format(aggregator))[1].split(")")[0]
    return "https://{}.com/game/{}/charts".format(aggregator, url_path)


def get_content(url):
    html = requests.get(url).content
    return BeautifulSoup(html, 'html.parser')


def get_ratings(content, aggregator):
    ratings = np.array([])
    if aggregator == 'opencritic':
        ratings_container = [rating.find("span") for rating in content.find_all('app-score-display')]
        for rating in ratings_container:
            if not rating.find("i") and "/" in rating.text:
                rating = float(rating.text.split("/")[0].strip()) * (10 / float(rating.text.split('/')[1].strip()))
                ratings = np.append(ratings, [rating])
    if aggregator == 'metacritic':
        ratings_container = [rating.find("div") for rating in content.find_all('div', class_='review_grade')]
        for rating in ratings_container:
            rating = float(rating.text) / 10
            ratings = np.append(ratings, [rating])
    ratings, counts = np.unique(ratings.astype(int), return_counts=True)
    scale = np.delete(np.arange(1, 11), ratings - 1)
    ratings = np.append(ratings, scale)
    counts = np.append(counts, np.zeros(len(scale)).astype(int))
    sort_idx = np.argsort(ratings)
    return ratings[sort_idx], counts[sort_idx]


def post_opencritic_scores(submission, aggregator):
    selftext = submission.selftext
    alternative = {'OpenCritic': 'MetaCritic', 'MetaCritic': 'OpenCritic'}
    if aggregator not in selftext:
        aggregator = alternative[aggregator]
    url = get_url_from_selftext(selftext, aggregator.lower())
    content = get_content(url)
    ratings, counts = get_ratings(content, aggregator.lower())
    title = content.find('h1').text
    metacritic_reply = '{} {} review spread at a glance:\n\n'.format(title, aggregator)
    print('{} {} review spread at a glance:'.format(title, aggregator))
    for r, c in zip(ratings[::-1], counts[::-1]):
        c = '|' * c
        metacritic_reply = metacritic_reply + '{:02d} - {}  \n'.format(r, c)
        print('{:02d} - {}'.format(r, c))
    metacritic_reply = metacritic_reply + '\n\nCredit: [gtafan6](https://www.reddit.com/r/Games/comments/dq0pdu/death_stranding_review_thread/f6031sc/)'
    print('^(Credit: [gtafan6](https://www.reddit.com/r/Games/comments/dq0pdu/death_stranding_review_thread/f6031sc/))')
    # submission['submission'].reply(metacritic_reply)
