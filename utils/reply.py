from utils.parsing import get_url_from_selftext, get_content, get_ratings
from utils.time import utc_time_now, get_date_str


def get_reply_body(submission, aggregator):
    selftext = submission.selftext
    if submission.selftext_html is None:
        selftext = submission.crosspost_parent_list[0]['selftext']
    alternative = {'OpenCritic': 'MetaCritic', 'MetaCritic': 'OpenCritic'}
    if aggregator.lower() not in selftext:
        aggregator = alternative[aggregator]
    url = get_url_from_selftext(selftext, aggregator.lower())
    content = get_content(url)
    title = content.find('h1').text
    ratings, counts = get_ratings(content, aggregator.lower())
    reply_body = '{} {} review spread at a glance:\n\n'.format(title, aggregator) + get_plot(ratings, counts)
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
