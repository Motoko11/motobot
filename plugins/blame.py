from motobot import command, sink, Priority
from random import choice


active_users = {}


@sink(priority=Priority.high)
def blame_sink(bot, database, nick, channel, message):
    global active_users
    l = active_users.get(channel, [])

    if len(l) < 100:
        l.append(nick)
    else:
        l.pop(0)
        l.append(nick)

    active_users[channel] = l


@command('blame')
def blame_command(bot, database, nick, channel, message, args):
    """ Blame the person who we all know did it! """
    global active_users
    return 'It was ' + choice(active_users.get(channel, [nick])) + '!'
