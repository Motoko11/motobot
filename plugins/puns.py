from motobot import command, match
from requests import get
from bs4 import BeautifulSoup


@command('joke')
@command('pun')
@match(r'(?:tell|give) (.+) a (.+)')
def pun_joke_command(bot, database, nick, channel, message, arg_match):
    """ These punny one liners sure to lighten up your day. """
    response = None
    type = None
    is_match = False

    if isinstance(arg_match, list):
        type = arg_match[0].lower()
    else:
        is_match = True
        type = arg_match.group(2).lower()

    if type == 'joke':
        response = get_joke()
    elif type == 'pun':
        response = get_pun()

    if is_match and response is not None:
        target = arg_match.group(1)
        targetless = ['us', 'me', 'them', 'him', 'her']

        if target.lower() not in targetless:
            response = "{}: {}".format(target, response)

    return response


def get_pun():
    url = 'http://www.punoftheday.com/cgi-bin/randompun.pl'
    bs = BeautifulSoup(get(url).text)
    pun = bs.find('p', recursive=True).text
    return pun


def get_joke():
    url = 'http://www.rinkworks.com/jokes/random.cgi'
    bs = BeautifulSoup(get(url).text)
    joke = bs.find_all('ul', recursive=True)[2].text.replace('\n', ' ').strip()
    return joke
