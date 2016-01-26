from motobot import command
from requests import get
from bs4 import BeautifulSoup


base_url = 'http://www.anime-planet.com'
results_cache = []


@command('stats')
def stats_command(bot, database, nick, channel, message, args):
    """ Return the stats link for #anime-planet.com. """
    if channel == '#anime-planet.com':
        stats_url = 'https://www.chalamius.se/stats/ap.html'
        return "Channel Stats: {}".format(stats_url)


@command('rr')
def rr_command(bot, database, nick, channel, message, args):
    """ Return the recommendations response. Takes single arg for target. """
    response = "If you are looking for anime/manga recommendations we have a database created specifically for that! Just visit www.anime-planet.com and let us do the hard work for you! For channel rules, please go to http://bit.ly/1aRaMhh"

    if len(args) > 1:
        response = "{}: {}".format(' '.join(args[1:]).strip(), response)

    return response


@command('mib')
def mib_command(bot, database, nick, channel, message, args):
    """ Help mibs get a real nick. Takes single arg for target. """
    response = "To change your nick to something you'd like type: /nick new_name; If you like that name and it is unregistered. To register it use: /ns REGISTER password [email]; More information can be found here: https://wiki.rizon.net/index.php?title=Register_your_nickname;"

    if len(args) > 1:
        response = "{}: {}".format(' '.join(args[1:]).strip(), response)

    return response

    
@command('a')
@command('anime')
def anime_search_command(bot, database, nick, channel, message, args):
    """ Search for an anime on anime-planet.com. """
    if len(args) > 1:
        return "Search result: {}".format(
            search_media(' '.join(args[1:]), 'anime'))
    else:
        return "Please supply a search term."


@command('m')
@command('manga')
def manga_search_command(bot, database, nick, channel, message, args):
    """ Search for a manga on anime-planet.com. """
    if len(args) > 1:
        return "Search result: {}".format(
            search_media(' '.join(args[1:]), 'manga'))
    else:
        return "Please supply a search term."


@command('u')
@command('user')
def user_search_command(bot, database, nick, channel, message, args):
    """ Search for a user on anime-planet.com. """
    format_str = "Search Results: {}"

    if len(args) > 1:
        return format_str.format(search_users(' '.join(args[1:])))
    else:
        return format_str.format(search_users(nick))


@command('c')
@command('char')
@command('character')
def character_search_command(bot, database, nick, channel, message, args):
    """ Search for a character on anime-planet.com. """
    if len(args) > 1:
        return "Search result: {}".format(
            search_characters(' '.join(args[1:])))
    else:
        return "Please supply a search term."


@command('rec')
@command('arec')
def anime_recommendations_search_command(bot, database, nick, channel, message, args):
    """ Search for an anime recommendation on anime-planet.com. """
    if len(args) > 1:
        return "Recommendations: {}".format(
            search_media(' '.join(args[1:]), 'anime', '/recommendations'))
    else:
        return "Please supply a search term."


@command('mrec')
def manga_recommendations_search_command(bot, database, nick, channel, message, args):
    """ Search for a manga recommendation on anime-planet.com. """
    if len(args) > 1:
        return "Recommendations: {}".format(
            search_media(' '.join(args[1:]), 'manga', '/recommendations'))
    else:
        return "Please supply a search term."


@command('top')
def top_anime_command(bot, database, nick, channel, message, args):
    """ Search for a user's lists on anime-planet.com. """
    format_str = "Top Anime: {}/lists"

    if len(args) > 1:
        return format_str.format(search_users(' '.join(args[1:])))
    else:
        return format_str.format(search_users(nick))


@command('more')
def more_command(bot, database, nick, channel, message, args):
    """ Return more results for the most recent anime-planet.com search. """
    try:
        return "More results: {}".format(results_cache.pop(0))
    except IndexError:
        return "There are no more results."


def search_media(term, type, append=''):
    global results_cache
    results_cache = []
    url = base_url + '/' + type + '/all?name=' + term.replace(' ', '%20')

    response = get(url)

    if response.url != url:
        return response.url + append
    else:
        bs = BeautifulSoup(response.text)

        if bs.find('div', {'class': 'error'}, recursive=True):
            return "No results found."
        else:
            results = bs.find_all('li', {'class': 'card'}, recursive=True)
            results_cache = [base_url + result.find('a')['href'] + append \
                for result in results]
            return results_cache.pop(0)


def search_users(user):
    user = user.rstrip()
    url = base_url + '/users/' + user.lower()

    response = get(url)

    if response.url.lower() != url:
        return "No users found with name '{}'.".format(user)
    else:
        return response.url


def search_characters(character):
    global results_cache
    results_cache = []
    url = base_url + '/characters/all?name=' + character.replace(' ', '%20')

    response = get(url)

    if response.url != url:
        return response.url
    else:
        bs = BeautifulSoup(response.text)

        if bs.find('div', {'class': 'error'}, recursive=True):
            return "No results found."
        else:
            results = bs.find_all('td', {'class': 'tableCharInfo'}, recursive=True)
            results_cache = [base_url + result.find('a')['href'] \
                for result in results]
            return results_cache.pop(0)


@command('worstcharacterofalltime')
def sothis_wishes(bot, database, nick, channel, message, args):
    """ Return the worse character of all time. So says sothis. """
    url = 'http://www.anime-planet.com/characters/makoto-itou'
    return "Behold, the worst anime character of all time, Makoto Itou! {}".format(url)
