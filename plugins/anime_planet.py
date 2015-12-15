from motobot import command
from requests import get
from bs4 import BeautifulSoup


@command('stats')
def stats_command(message, database):
    stats_url = 'https://www.chalamius.se/stats/ap.html'
    return "Channel Stats: {}".format(stats_url)


@command('rr')
def rr_command(message, database):
    response = "If you are looking for anime/manga recommendations we have a database created specifically for that! Just visit www.anime-planet.com and let us do the hard work for you! For channel rules, please go to http://bit.ly/1aRaMhh"

    args = message.message.split(' ')

    if len(args) > 1:
        response = "{}: {}".format(' '.join(args[1:]).strip(), response)

    return response

    
@command('a')
@command('anime')
def anime_search_command(message, database):
    args = message.message.split(' ')

    if len(args) > 1:
        return "Search result: {}".format(
            search_media(' '.join(args[1:]), 'anime'))
    else:
        return "Please supply a search term."


@command('m')
@command('manga')
def manga_search_command(message, database):
    args = message.message.split(' ')

    if len(args) > 1:
        return "Search result: {}".format(
            search_media(' '.join(args[1:]), 'manga'))
    else:
        return "Please supply a search term."


@command('u')
@command('user')
def user_search_command(message, database):
    args = message.message.split(' ')
    format_str = "Search Results: {}"

    if len(args) > 1:
        return format_str.format(search_users(' '.join(args[1:])))
    else:
        return format_str.format(search_users(message.nick))


@command('rec')
@command('arec')
def anime_recommendations_search_command(message, database):
    args = message.message.split(' ')

    if len(args) > 1:
        return "Recommendations: {}/recommendations".format(
            search_media(' '.join(args[1:]), 'anime'))
    else:
        return "Please supply a search term."


@command('mrec')
def manga_recommendations_search_command(message, database):
    args = message.message.split(' ')

    if len(args) > 1:
        return "Recommendations: {}/recommendations".format(
            search_media(' '.join(args[1:]), 'manga'))
    else:
        return "Please supply a search term."


@command('top')
def top_anime_command(message, database):
    args = message.message.split(' ')
    format_str = "Top Anime: {}/lists"

    if len(args) > 1:
        return format_str.format(search_users(' '.join(args[1:])))
    else:
        return format_str.format(search_users(message.nick))


def search_media(term, type):
    base_url = 'http://www.anime-planet.com'
    url = base_url + '/' + type + '/all?name=' + term.replace(' ', '%20')

    response = get(url)

    if response.url != url:
        return response.url
    else:
        bs = BeautifulSoup(response.text)

        if bs.find('div', {'class': 'error'}, recursive=True):
            return "No results found."
        else:
            result = bs.find('li', {'class': 'card'}, recursive=True)
            return base_url + result.find('a')['href']


def search_users(user):
    base_url = 'http://www.anime-planet.com'
    user = user.rstrip()
    url = base_url + '/users/' + user.lower()

    response = get(url)

    if response.url.lower() != url:
        return "No users found with name '{}'.".format(user)
    else:
        return response.url
