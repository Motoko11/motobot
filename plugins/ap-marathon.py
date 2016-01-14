from motobot import command
from requests import get
from bs4 import BeautifulSoup
from time import time
from re import sub


url = 'https://marathon.chalamius.se/'


marathon_cache = {
    'time': 0,
    'title': '',
    'date': '',
    'link': '',
    'note': ''
}


@command('marathonlist')
def marathonlist_command(bot, message, database):
    return "The marathon list can be found at {}.".format(url)


@command('marathon')
def marathon_command(bot, message, database):
    title, date, link, note = get_current_marathon()
    return "Today's marathon ({}) is {} ({}) {}".format(
        date, title, link, note
    )


def get_current_marathon():
    global marathon_cache

    if marathon_cache['time'] < time():
        bs = BeautifulSoup(get(url).text)

        entries = bs.find_all('tr', recursive=True)
        entry = entries[-1]

        title_cell = entry.find('td', {'class', 'anime-title'})
        date_call = entry.find('td', {'class', 'anime-date'})
        note_cell = entry.find('td', {'class', 'anime-note'})

        marathon_cache['title'] = chala_protection(title_cell.text)
        marathon_cache['date'] = chala_protection(date_call.text)
        marathon_cache['link'] = chala_protection(title_cell.find('a')['href'])
        marathon_cache['note'] = chala_protection(note_cell.text)
        marathon_cache['time'] = time() + 60 * 60

    return (marathon_cache['title'], marathon_cache['date'],
            marathon_cache['link'], marathon_cache['note'])


def chala_protection(string):
    return sub(r'[^\S ]+', '', string).strip()


@command('pantsu')
@command('pants')
@command('panties')
def pants_command(bot, message, database):
    url = 'https://www.youtube.com/watch?v=T_tAoo787q4'
    title = 'Sora no Otoshimono #2 Creditless ED'
    return 'Panties! {} - {}'.format(title, url)
