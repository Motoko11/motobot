from motobot import command, sink, Priority, IRCLevel, Notice
from random import choice


active_users = {}
next_blame = None


@sink(priority=Priority.high)
def blame_sink(bot, context, message):
    global active_users
    l = active_users.get(context.channel, [])

    if len(l) < 100:
        l.append(context.nick)
    else:
        l.pop(0)
        l.append(context.nick)

    active_users[context.channel] = l


@command('blame')
def blame_command(bot, context, message, args):
    """ Blame the person who we all know did it! """
    global active_users
    global next_blame
    target = ''

    if next_blame is None:
        target = choice(active_users.get(context.channel, [context.nick]))
    else:
        target = next_blame
        next_blame = None

    return 'It was ' + target + '!'


@command('setblame', level=IRCLevel.master)
@command('nextblame', level=IRCLevel.master)
def setblame_command(bot, context, message, args):
    global next_blame
    response = ''
    try:
        target = ' '.join(args[1:])
        next_blame = target
        response = "Next blame set to blame {}.".format(target)
    except IndexError:
        response = "Error: Please supply a user to blame."
    return response, Notice(context.nick)
