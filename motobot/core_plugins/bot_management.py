from motobot import command, hook, Notice, IRCLevel, Command, Target, Action


@command('command', level=IRCLevel.master)
def command_command(bot, database, nick, channel, message, args):
    """ Command to manage the basic functions of the bot.

    The 'join' and 'part' argument both require a channel argument.
    The 'quit' and 'part' argument has an optional quit/part message.
    The 'show' argument will return a list of currently joined channels.
    The 'set' argument will set an attribute of the bot. Use with caution.
    The 'say' command is also accessible through an argument this command.
    """
    response = None
    notice = Notice(nick)

    try:
        arg = args[1].lower()

        if arg == 'join':
            channel = args[2]
            response = join_channel(database, channel, notice)
        elif arg == 'part':
            channel = args[2]
            message = args[3:]
            response = part_channel(database, channel, message, notice)
        elif arg == 'quit':
            message = args[2:]
            response = quit(bot, message, notice)
        elif arg == 'show':
            response = show_channels(database, notice)
        elif arg == 'say':
            target = args[2]
            message = ' '.join(args[3:])
            response = say(target, message)
        elif arg == 'set':
            name = args[2]
            value = args[3:]
            response = set_val(bot, name, value, notice)
        else:
            response = ("Error: Invalid argument.", notice)
    except IndexError:
        response = ("Error: Too few arguments supplied.", notice)

    return response


@command('say', level=IRCLevel.master)
def say_command(bot, database, nick, channel, message, args):
    """ Send a message to a given target.

    Usage: say <TARGET> [MESSAGE]
    """
    try:
        target = args[1]
        message = ' '.join(args[2:])
        return say(target, message)
    except IndexError:
        return ("Error: Too few arguments supplied.", Notice(nick))


def join_channel(database, channel, notice):
    response = None
    channels = database.get_val(set())

    if channel.lower() in channels:
        response = ("I'm already in {}.".format(channel, notice))
    else:
        channels.add(channel.lower())
        database.set_val(channels)
        response = [
            Command('JOIN', channel),
            ("I have joined {}.".format(channel), notice)
        ]
    return response


def part_channel(database, channel, message, notice):
    response = None
    channels = database.get_val(set())

    if channel.lower() not in channels:
        response = ("I'm not in {}.".format(channel, notice))
    else:
        channels.discard(channel.lower())
        database.set_val(channels)
        response = [
            message, Command('PART', channel),
            ("I have left {}.".format(channel), notice)
        ]
    return response


def quit(bot, message, notice):
    bot.running = bot.connected = bot.identified = False
    return [
        ("Goodbye!", notice),
        (message, Command('QUIT'))
    ]


def show_channels(database, notice):
    channels = database.get_val(set())
    return (notice, "I am currently in: {}.".format(', '.join(channels)))


def say(target, message):
    target_modifier = Target(target)
    if message.startswith('/me '):
        return (message[4:], target_modifier, Action)
    else:
        return (message, target_modifier)


def set_val(bot, name, value, notice):
    return ("This function has not yet been implemeneted.", notice)


@hook('004')
def handling_joining_channels(bot, message):
    database = bot.database.get_entry(__name__)
    channels = database.get_val(set())
    channels |= set(map(lambda x: x.lower(), bot.channels))
    database.set_val(channels)

    for channel in channels:
        bot.send('JOIN ' + channel)
