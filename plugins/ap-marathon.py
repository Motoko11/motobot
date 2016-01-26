from motobot import command
from requests import get
from bs4 import BeautifulSoup
from time import time
from re import sub

base_url = 'https://marathon.chalamius.se/'

@command('marathonlist')
def marathonlist_command(bot, database, nick, channel, message, args):
    """ Return the marathon website. """
    return "The marathon list can be found at {}.".format(base_url)


@command('marathon')
def marathon_command(bot, database, nick, channel, message, args):
    """ Return details of the current show on the marathon list. """
    title, date, link, note = get_current_marathon()
    return "Today's marathon ({}) is {} ({}) {}".format(
        date, title, link, note
    )


def get_current_marathon():
    url = base_url + 'calendar.json'
    entries = get(url).json()['items']
    entry = entries[-1]
    return entry['name'], entry['date'], entry['url'], entry['note']


@command('pantsu')
@command('pants')
@command('panties')
def pants_command(bot, database, nick, channel, message, args):
    """ PANTIES! Need moar? """
    url = 'https://www.youtube.com/watch?v=T_tAoo787q4'
    title = 'Sora no Otoshimono #2 Creditless ED'
    return '{}! {} - {}'.format(args[0].capitalize(), title, url)


@command('bewbs')
@command('boobs')
@command('boobies')
def boobs_command(bot, database, nick, channel, message, args):
    """ BOOBS! Need moar? """
    url = 'https://www.youtube.com/watch?v=Pw5lu06LvH4'
    title = 'Oppai Dragon Song'
    return '{}! {} - {}'.format(args[0].capitalize(), title, url)


@command('butts')
def butts_command(bot, database, nick, channel, message, args):
    """ BUTTS! Need moar? """
    url = 'http://i219.photobucket.com/albums/cc65/_chii69_/AnimalButts.jpg'
    return '{}! {}'.format(args[0].capitalize(), url)
