from motobot import command, match, IRCLevel
from random import uniform, normalvariate


def generate_spam(str):
    """ The needless variables are for later, when stats are added. """
    un = uniform(0, 1) < 0.01
    number = int(round(normalvariate(10, 3)))
    string = 'un' + str if un else str * number
    return un, number, string


@match(r'^desu( *)$')
def desu_match(message, database):
    un, number, string = generate_spam('desu')
    return string


@match(r'^baka( *)$', IRCLevel.op)
def baka_match(message, database):
    un, number, string = generate_spam('baka')
    return string


@match(r'^nya(a+)?n*?(\W|$)')
def nyan_match(message, database):
    num = int(round(normalvariate(15, 3)))
    return 'Ny' + 'a' * num + '~'


@command('desu')
@command('desustats')
def desu_command(message, database):
    return "Provisional command for desu stats."
