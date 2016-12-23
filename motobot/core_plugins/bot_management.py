from motobot import command, hook, Notice, IRCLevel, Command, Target, Action, Priority, split_response


def get_channels(database):
    return set(database.get([]))


def set_channels(database, channels):
    return database.set(list(channels))


@command('command', level=IRCLevel.master, priority=Priority.max)
def command_command(bot, context, message, args):
    """ Command to manage the basic functions of the bot.

    Valid arguments are: 'join', 'part', 'quit', 'show', 'reconnect' and 'reload'.
    The 'join' and 'part' argument both require a channel argument.
    The 'join' command has an optional channel password argument.
    The 'quit', 'part', and 'reconnect' argument have an optional quit/part message.
    The 'show' argument will return a list of currently joined channels.
    The 'reload' command will reload the plugins in the loaded packages.
    """
    try:
        arg = args[1].lower()

        if arg == 'join':
            channel = ' '.join(args[2:])
            response = join_channel(context.database, channel)
        elif arg == 'part':
            channel = args[2]
            message = ' '.join(args[3:])
            response = part_channel(context.database, channel, message)
        elif arg == 'quit':
            bot.running = False
            message = ' '.join(args[2:])
            response = quit(message)
        elif arg == 'reconnect':
            message = ' '.join(args[2:])
            response = quit(message)
        elif arg == 'show':
            response = show_channels(context.database)
        elif arg == 'reload':
            error = bot.reload_plugins()
            response = "Plugins have been reloaded." + \
                (" There were some errors." if error else "")
        else:
            response = "Error: Invalid argument."
    except IndexError:
        response = "Error: Too few arguments supplied."

    return response, Notice(context.nick)


@command('channel', level=IRCLevel.master, priority=Priority.max)
def channel_command(bot, context, message, args):
    """ Override the channel to make a command act as if it were in another channel. """
    try:
        channel = args[1]
        if channel.lower() in get_channels(context.database):
            message = ' '.join(args[2:])
            response = bot.request('HANDLE_MESSAGE', context.nick, channel, context.host, message)
        else:
            response = "Error: Please provide a channel that I'm currently in.", Notice(context.nick)
    except IndexError:
        response = "Error: Please provide a channel.", Notice(context.nick)
    return response


@command('say', level=IRCLevel.master)
def say_command(bot, context, message, args):
    """ Send a message to a given target.

    Usage: say <TARGET> [MESSAGE]
    """
    try:
        target = args[1]
        message = ' '.join(args[2:])
        return say(target, message)
    except IndexError:
        return ("Error: Too few arguments supplied.", Notice(context.nick))


@command('raw', level=IRCLevel.master)
def raw_command(bot, context, message, args):
    """ Send a raw IRC message to the server. """

    bot.send(' '.join(args[1:]))


def join_channel(database, channel):
    response = None
    channels = get_channels(database)

    if channel.lower() in channels:
        response = "I'm already in {}.".format(channel)
    else:
        channels.add(channel.lower())
        set_channels(database, channels)
        response = (
            [Command('JOIN', channel)],
            "I have joined {}.".format(channel)
        )
    return response


def part_channel(database, channel, message):
    response = None
    channels = get_channels(database)

    if channel.lower() not in channels:
        response = "I'm not in {}.".format(channel)
    else:
        channels.discard(channel.lower())
        set_channels(database, channels)
        response = [
            (message, Command('PART', channel)),
            "I have left {}.".format(channel)
        ]
    return response


def quit(message):
    return ("Goodbye!", (message, Command('QUIT', [])))


def show_channels(database):
    channels = map(lambda x: x.split(' ', 1)[0], get_channels(database))
    return split_response(channels, "I am currently in: {}")


def say(target, message):
    target_modifier = Target(target)
    if message.startswith('/me '):
        return (message[4:], target_modifier, Action)
    else:
        return (message, target_modifier)


@hook('KICK')
def handle_kick(bot, context, message):
    if message.params[1] == bot.nick:
        channel = message.params[0]
        part_channel(context.database, channel, None)


@hook('004')
def handling_joining_channels(bot, context, message):
    channels = get_channels(context.database)
    channels |= set(map(lambda x: x.lower(), bot.channels))
    set_channels(context.database, channels)

    for channel in channels:
        bot.send('JOIN ' + channel)
