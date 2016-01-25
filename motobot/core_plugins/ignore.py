from motobot import hook, command, sink, Priority, IRCLevel, Eat, Command
from collections import namedtuple


def add_ignore(modifier, database, channel, nick):
    response = ''
    ignores = database.get_val({})
    channel_ignores = ignores.get(channel, set())

    if nick.lower() in channel_ignores:
        response = "I'm already ignoring {}.".format(nick)
    else:
        channel_ignores.add(nick.lower())
        ignores[channel] = channel_ignores
        database.set_val(ignores)
        response = "I'm now ignoring {}.".format(nick)
    return response, modifier


def del_ignore(modifier, database, channel, nick):
    responses = ''
    ignores = database.get_val({})
    channel_ignores = ignores.get(channel, set())

    if nick.lower() not in channel_ignores:
        response = "I'm not ignoring {}.".format(nick)
    else:
        channel_ignores.discard(nick.lower())
        ignores[channel] = channel_ignores
        database.set_val(ignores)
        response = "I'm no longer ignoring {}.".format(nick)
    return response, modifier


def show_ignores(modifier, database, channel):
    channel_ignores = database.get_val({}).get(channel, set())
    if channel_ignores == set():
        return "I am not ignoring anyone on {}.".format(channel)
    else:
        return "I am currently ignoring: {} on {}.".format(
            ", ".join(channel_ignores), channel)


@command('ignore', priority=Priority.max, level=IRCLevel.hop)
def ignore_command(bot, database, nick, channel, message, args):
    response = ''
    modifier = Command('NOTICE', [nick])

    try:
        arg = args[1].lower()
        if arg == 'add':
            response = add_ignore(modifier, database, channel, args[2])
        elif arg == 'del' or arg == 'rem':
            response = del_ignore(modifier, database, channel, args[2])
        elif arg == 'all':
            response = ignoreall(channel)
        elif arg == 'show':
            response = show_ignores(modifier, database, channel)
        else:
            response = ('Error: Invalid argument;', modifier)
    except IndexError:
        response = ("Not enough arguments provided.", modifier)
    return response


ignoring_all = set()


def ignoreall(channel):
    global ignoring_all
    response = None
    if channel in ignoring_all:
        ignoring_all.discard(channel)
        response = "I am no longer ignoring everyone in {}.".format(channel)
    else:
        ignoring_all.add(channel)
        response = "I am now ignoring everyone in {}.".format(channel)
    return response


def ignore_sink(bot, database, nick, channel, message):
    channel_ignores = database.get_val({}).get(channel, set())
    if nick.lower() in channel_ignores:
        return Eat


@sink(priority=Priority.max, level=IRCLevel.hop, alt=ignore_sink)
def hop_ignore_sink(bot, database, nick, channel, message):
    return None


def ignoreall_sink(bot, database, nick, channel, message):
    global ignoring_all
    if channel in ignoring_all:
        return Eat


@sink(priority=Priority.max, level=IRCLevel.hop, alt=ignoreall_sink)
def hop_ignoreall_sink(bot, database, nick, channel, message):
    return None
