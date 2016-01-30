from motobot import command, sink, Priority, IRCLevel, Notice
from random import choice


active_users = {}
next_blame = None


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
    global next_blame
    target = ''

    if next_blame is None:
        target = choice(active_users.get(channel, [nick]))
    else:
        target = next_blame
        next_blame = None

    return 'It was ' + target + '!'


@command('setblame', level=IRCLevel.master)
@command('nextblame', level=IRCLevel.master)
def setblame_command(bot, database, nick, channel, message, args):
    global next_blame
    notice = Notice(nick)
    try:
        target = ' '.join(args[1:])
        next_blame = target
        return "Next blame set to blame {}.".format(target), notice
    except IndexError:
        return "Error: Please supply a user to blame."
