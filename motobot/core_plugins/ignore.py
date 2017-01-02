from motobot import command, sink, Priority, IRCLevel, Eat, Notice, split_response


@command('ignore', priority=Priority.max, level=IRCLevel.hop)
def ignore_command(bot, context, message, args):
    """ Manage ignores in a channel.

    Valid arguments are: 'add', 'del', 'all, and 'show'.
    'add' and 'del' require a nick argument.
    'all' will toggle ignoring for the entire channel on and off.
    'show' will show the currently ignored nicks in the channel.
    """
    response = ''
    try:
        arg = args[1].lower()
        if arg == 'add':
            response = add_ignore(context.database, context.channel, args[2])
        elif arg == 'del' or arg == 'rem':
            response = del_ignore(context.database, context.channel, args[2])
        elif arg == 'all':
            response = ignoreall(context.channel)
        elif arg == 'show':
            response = show_ignores(context.database, context.channel)
        else:
            response = 'Error: Invalid argument;'
    except IndexError:
        response = "Not enough arguments provided."
    return response, Notice(context.nick)


def add_ignore(database, channel, nick):
    ignores = database.get({})
    channel_ignores = ignores.get(channel, [])

    if nick.lower() in channel_ignores:
        response = "I'm already ignoring {} on {}.".format(nick, channel)
    else:
        channel_ignores.append(nick.lower())
        ignores[channel] = channel_ignores
        database.set(ignores)
        response = "I'm now ignoring {} on {}.".format(nick, channel)
    return response


def del_ignore(database, channel, nick):
    ignores = database.get({})
    channel_ignores = ignores.get(channel, [])

    try:
        channel_ignores.remove(nick.lower())
        ignores[channel] = channel_ignores
        database.set(ignores)
        response = "I'm no longer ignoring {} on {}.".format(nick, channel)
    except KeyError:
        response = "I'm not ignoring {} on {}.".format(nick, channel)
    return response


def show_ignores(database, channel):
    channel_ignores = database.get({}).get(channel, [])

    if channel_ignores:
        response = split_response(
            channel_ignores, "I am currently ignoring: {} on {}".format('{}', channel))
    else:
        response = "I am not ignoring anyone on {}.".format(channel)

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


def ignore_sink(bot, context, message):
    channel_ignores = context.database.get({}).get(context.channel, [])
    if context.nick.lower() in channel_ignores:
        return Eat


@sink(priority=Priority.max, level=IRCLevel.hop, alt=ignore_sink)
def hop_ignore_sink(bot, context, message):
    return None


def ignoreall_sink(bot, context, message):
    global ignoring_all
    if context.channel in ignoring_all:
        return Eat


@sink(priority=Priority.max, level=IRCLevel.hop, alt=ignoreall_sink)
def hop_ignoreall_sink(bot, context, message):
    return None
