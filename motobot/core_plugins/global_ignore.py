from motobot import command, sink, Priority, IRCLevel, Eat, Notice, split_response


def get_ignores(database):
    return set(database.get([]))


def set_ignores(database, ignores):
    return database.set(list(ignores))


@command('globalignore', priority=Priority.max, level=IRCLevel.master)
def globalignore_command(bot, context, message, args):
    """ Manage global ignores.

    Valid arguments are: 'add', 'del', 'all, and 'show'.
    'add' and 'del' require a nick argument.
    'show' will show the currently ignored nicks in the channel.
    """
    response = ''
    try:
        arg = args[1].lower()
        if arg == 'add':
            response = add_ignore(context.database, context.channel, args[2])
        elif arg == 'del' or arg == 'rem':
            response = del_ignore(context.database, context.channel, args[2])
        elif arg == 'show':
            response = show_ignores(context.database, context.channel)
        else:
            response = 'Error: Invalid argument;'
    except IndexError:
        response = "Not enough arguments provided."
    return response, Notice(context.nick)


def add_ignore(database, channel, nick):
    ignores = get_ignores(database)

    if nick.lower() in ignores:
        response = "I'm already ignoring {}.".format(nick)
    else:
        ignores.add(nick.lower())
        set_ignores(database, ignores)
        response = "I'm now ignoring {}.".format(nick)
    return response


def del_ignore(database, channel, nick):
    ignores = get_ignores(database)

    try:
        ignores.remove(nick.lower())
        set_ignores(database, ignores)
        response = "I'm no longer ignoring {}.".format(nick)
    except KeyError:
        response = "I'm not ignoring {}.".format(nick)
    return response


def show_ignores(database, channel):
    ignores = get_ignores(database)

    if ignores:
        response = split_response(ignores, "I am currently ignoring: {}.")
    else:
        response = "I am not ignoring anyone."

    return response


def globalignore_sink(bot, context, message):
    ignores = get_ignores(context.database)
    if context.nick.lower() in ignores:
        return Eat


@sink(priority=Priority.max, level=IRCLevel.master, alt=globalignore_sink)
def master_globalignore_sink(bot, context, message):
    return None
