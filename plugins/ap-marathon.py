from motobot import command
from requests import get
from bs4 import BeautifulSoup
from time import time


marathon_cache = {
    'time': 0,
    'title': '',
    'link': '',
    'note': ''
}


@command('marathon')
def marathon_command(bot, message, database):
    title, link, note = get_current_marathon()
    return "Today's marathon is {} ({}) {}".format(title, link, note)


def get_current_marathon():
    global marathon_cache

    if marathon_cache['time'] < time():
        print("Cache reloaded")
        url = 'https://marathon.chalamius.se/'
        bs = BeautifulSoup(get(url).text)

        entries = bs.find_all('tr', recursive=True)
        entry = entries[-1]

        title_cell = entry.find('td', {'class', 'anime-title'})
        note_cell = entry.find('td', {'class', 'anime-note'})

        marathon_cache['title'] = title_cell.text
        marathon_cache['link'] = title_cell.find('a')['href']
        marathon_cache['note'] = note_cell.text
        marathon_cache['time'] = time() + 60 * 60

    return (marathon_cache['title'], marathon_cache['link'], marathon_cache['note'])