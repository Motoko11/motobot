from motobot import match
from random import randint


@match(r'hentai')
def noda_match(bot, nick, channel, message, match):
    valid = ['nodame-chan', 'nodanyan', 'moto-chan', 'otakuhime']
    if nick.lower() in valid:
        return 'hentai' * randint(1, 15)
