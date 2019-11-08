import requests
import numpy as np

from bs4 import BeautifulSoup


__author__ = 'https://github.com/lebeli'
__copyright__ = 'Copyright 2019'
__license__ = 'MPL 2.0'
__version__ = '0.1.0'
__maintainer__ = 'https://github.com/lebeli'
__status__ = 'Dev'


def get_url_from_selftext(selftext, aggregator):
    url_path = selftext.split("{}.com/game/".format(aggregator))[1].split(")")[0]
    if aggregator == 'opencritic':
        url = "https://{}.com/game/{}/charts".format(aggregator, url_path)
    if aggregator == 'metacritic':
        url = "https://www.{}.com/game/{}/critic-reviews".format(aggregator, url_path)
    return url


def get_content(url):
    html = ''
    while html == '':
        try:
            html = requests.get(url).content
        except requests.exceptions.ConnectionError:
            print('Connection denied.')
            headers = {
                'Referer': 'https://itunes.apple.com',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
            }
            html = requests.get(url, headers=headers).content
    return BeautifulSoup(html, 'html.parser')


def get_ratings(content, aggregator):
    ratings = np.array([])
    if aggregator == 'opencritic':
        ratings_containers = [rating.find("app-score-display") for rating in content.find_all('div', class_='review-box')]
        for ratings_container in ratings_containers:
            if ratings_container.find("i"):
                rating = (10 / len(ratings_container.find_all("i")))*(len(ratings_container.find_all('i', class_='fas fa-star')) + \
                         0.5 * len(ratings_container.find_all('i', class_='fas fa-star-half-alt')))
                ratings = np.append(ratings, [rating])
            if not ratings_container.find("i") and any(t.isdigit() for t in ratings_container.text):
                # in ratings_container.text:
                rating = float(ratings_container.text.split("/")[0].strip()) * (10 / float(ratings_container.text.split('/')[1].strip()))
                ratings = np.append(ratings, [rating])
    if aggregator == 'metacritic':  # TODO: fix parsing
        ratings_containers = [rating.find("div") for rating in content.find_all('div', class_='review_grade')]
        for ratings_container in ratings_containers:
            rating = float(ratings_container.text) / 10
            ratings = np.append(ratings, [rating])
    ratings, counts = np.unique(ratings.astype(int), return_counts=True)
    scale = np.delete(np.arange(1, 11), ratings - 1)
    ratings = np.append(ratings, scale)
    counts = np.append(counts, np.zeros(len(scale)).astype(int))
    sort_idx = np.argsort(ratings)
    return ratings[sort_idx], counts[sort_idx]
