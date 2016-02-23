from motobot import command
from random import uniform


poopkey = 'poop'
poopchange = 10


@command('poop')
def poop_command(bot, context, message, args):
    return ' '.join(poop(args[1:]))


@command('setpoop')
def setpoop_command(bot, context, message, args):
    global poopkey
    response = None
    if len(args[1:]) != 0:
        poopkey = ' '.join(args[1:])
        response = 'Poop key set to {}.'.format(poopkey)
    else:
        response = 'Poop key currently set to {}.'.format(poopkey)
    return response


def poop(words):
    for word in words:
        if uniform(0, 100) <= poopchange:
            yield poopkey
        else:
            yield word

