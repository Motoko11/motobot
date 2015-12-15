from motobot import command
from requests import get
from bs4 import BeautifulSoup
from time import time


marathon_cache = (0, '', '')


@command('marathon')
def marathon_command(message, database):
    title, link = get_current_marathon()
    return "Today's marathon is {} ({})".format(title, link)


def get_current_marathon():
    global marathon_cache

    if marathon_cache[0] < time():
        print("Cache reloaded")
        url = 'https://marathon.chalamius.se/'
        bs = BeautifulSoup(get(url).text)

        entries = bs.find_all('td', {'class', 'anime-title'}, recursive=True)
        entry = entries[-1]

        title = entry.text.strip()
        link = entry.find('a')['href']
        marathon_cache = (time() + 60 * 60, title, link)

    return (marathon_cache[1], marathon_cache[2])