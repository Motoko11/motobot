from motobot import command, sink, Priority, IRCLevel, Eat, Notice, split_response, hostmask_check


@command('ignore', priority=Priority.max, level=IRCLevel.hop)
def ignore_command(bot, context, message, args):
    try:
        response = add_ignore(context.database, context.channel, args[1])
    except IndexError:
        response = "Error: Please provide a mask or nick to ignore."
    return response, Notice(context.nick)


@command('unignore', priority=Priority.max, level=IRCLevel.hop)
def unignore_command(bot, context, message, args):
    try:
        response = del_ignore(context.database, context.channel, args[1])
    except IndexError:
        response = "Error: Please provide a mask or nick to unignore."
    return response, Notice(context.nick)


@command('ignorelist', priority=Priority.max, level=IRCLevel.hop)
def ignorelist_command(bot, context, message, args):
    return show_ignores(context.database, context.channel), Notice(context.nick)


@command('ignoreall', priority=Priority.max, level=IRCLevel.hop)
def ignoreall_command(bot, context, message, args):
    return ignoreall(context.channel)


def nick_to_mask(mask):
    if '!' not in mask and '@' not in mask:
        mask += '!*@*'
    return mask.lower()


def add_ignore(database, channel, nick):
    ignores = database.get({})
    channel_ignores = ignores.get(channel, [])
    mask = nick_to_mask(nick)

    if mask in channel_ignores:
        response = "I'm already ignoring {} on {}.".format(nick, channel)
    else:
        channel_ignores.append(mask)
        ignores[channel] = channel_ignores
        database.set(ignores)
        response = "I'm now ignoring {} on {}.".format(mask, channel)
    return response


def del_ignore(database, channel, nick):
    ignores = database.get({})
    channel_ignores = ignores.get(channel, [])
    mask = nick_to_mask(nick)

    try:
        channel_ignores.remove(mask)
        ignores[channel] = channel_ignores
        database.set(ignores)
        response = "I'm no longer ignoring {} on {}.".format(mask, channel)
    except ValueError:
        response = "I'm not ignoring {} on {}.".format(mask, channel)
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
    for mask in channel_ignores:
        if hostmask_check(context.nick, context.host, mask):
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
