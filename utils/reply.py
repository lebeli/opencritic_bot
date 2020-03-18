import requests

from utils.parsing import get_ratings
from utils.time import utc_time_now, get_date_str
from bs4 import BeautifulSoup
from exceptions.server import InternalServerError


def get_url_from_selftext(selftext):
    url_path = selftext.split("opencritic.com/game/")[1].split(")")[0]
    return "https://opencritic.com/game/{}/charts".format(url_path)


def get_content(url):
    html = ''
    while html == '':
        try:
            r = requests.get(url)
            if r.status_code != 200:
                raise InternalServerError
            html = r.content
        except requests.exceptions.ConnectionError:
            print('Connection denied.')
    return BeautifulSoup(html, 'html.parser')


def get_reply_body(submission):
    selftext = submission.selftext
    if submission.selftext_html is None and submission.crosspost_parent_list:
        selftext = submission.crosspost_parent_list[0]['selftext']
    url = get_url_from_selftext(selftext)
    content = get_content(url)
    title = content.find('h1').text
    ratings, counts = get_ratings(content)
    reply_body = '{} OpenCritic review spread at a glance:\n\n'.format(title) + get_plot(ratings, counts)
    return reply_body + '\n\n'


def get_reply_footer():
    return '^Credit: ^[gtafan6](https://www.reddit.com/r/Games/comments/dq0pdu/death_stranding_review_thread/f6031sc/)'\
           + '  \n^[github](https://github.com/lebeli/opencritic_bot)\n\n'


def get_reply_edit_time(dt):
    return '^^Last ^^update {} ^^{}:{:02d} ^^UTC'.format(get_date_str(utc_time_now()), dt.hour, dt.minute)


def get_plot(label, value):
    plot = ''
    for l, v in zip(label[::-1], value[::-1]):
        bar = '▨' * v
        if len(bar) > 0:
            plot = plot + '    {:02d} - {} {}  \n'.format(l, bar, v)
        else:
            plot = plot + '    {:02d} - {}  \n'.format(l, bar)
    return plot
