from motobot import match
from random import randint


@match(r'hentai')
def noda_match(message, database):
    valid = ['nodame-chan', 'nodanyan', 'moto-chan', 'otakuhime']
    if message.nick.lower() in valid:
        return 'hentai' * randint(1, 15)
