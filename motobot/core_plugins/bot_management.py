from motobot import command, hook, Notice, IRCLevel, Command, Target, Action


@command('command', level=IRCLevel.master)
def command_command(bot, context, message, args):
    """ Command to manage the basic functions of the bot.

    The 'join' and 'part' argument both require a channel argument.
    The 'join' command has an optional channel password argument.
    The 'quit', 'part', and 'reconnect' argument have an optional quit/part message.
    The 'show' argument will return a list of currently joined channels.
    The 'set' argument will set an attribute of the bot. Use with caution.
    The 'reload' command will reload the plugins in the loaded packages.
    """
    response = None

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
        elif arg == 'set':
            name = args[2]
            value = args[3:]
            response = set_attribute(bot, name, value)
        elif arg == 'reload':
            error = bot.reload_plugins()
            response = "Plugins have been reloaded." + \
                (" There were some errors." if error else "")
        else:
            response = "Error: Invalid argument."
    except IndexError:
        response = "Error: Too few arguments supplied."

    return response, Notice(context.nick)


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


def join_channel(database, channel):
    response = None
    channels = database.get(set())

    if channel.lower() in channels:
        response = "I'm already in {}.".format(channel)
    else:
        channels.add(channel.lower())
        database.set(channels)
        response = (
            [Command('JOIN', channel)],
            "I have joined {}.".format(channel)
        )
    return response


def part_channel(database, channel, message):
    response = None
    channels = database.get(set())

    if channel.lower() not in channels:
        response = "I'm not in {}.".format(channel)
    else:
        channels.discard(channel.lower())
        database.set(channels)
        response = [
            (message, Command('PART', channel)),
            "I have left {}.".format(channel)
        ]
    return response


def quit(message):
    return [
        "Goodbye!",
        (message, Command('QUIT', []))
    ]


def show_channels(database):
    channels = database.get(set())
    return "I am currently in: {}.".format(', '.join(channels))


def say(target, message):
    target_modifier = Target(target)
    if message.startswith('/me '):
        return (message[4:], target_modifier, Action)
    else:
        return (message, target_modifier)


def set_attribute(bot, name, value):
    return "This function has not yet been implemeneted."


@hook('KICK')
def handle_kick(bot, message):
    if message.params[1] == bot.nick:
        database = bot.database.get_entry(__name__)
        channel = message.params[0]
        part_channel(database, channel, None)


@hook('004')
def handling_joining_channels(bot, message):
    database = bot.database.get_entry(__name__)
    channels = database.get(set())
    channels |= set(map(lambda x: x.lower(), bot.channels))
    database.set(channels)

    for channel in channels:
        bot.send('JOIN ' + channel)
