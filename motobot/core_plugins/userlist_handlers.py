from motobot import hook, request, command, IRCLevel, Notice


@command('levelprobe')
def levelprobe_command(bot, context, message, args):
    try:
        nick = args[1]
        mapping = {
            IRCLevel.user: "Regular User",
            IRCLevel.voice: "Voice",
            IRCLevel.hop: "Half-op",
            IRCLevel.aop: "Op",
            IRCLevel.sop: "Protected Op",
            IRCLevel.owner: "Owner",
            IRCLevel.master: "Bot Admin",
        }
        level = bot.request('USERLEVEL', context.channel, nick)
        return "{} is a {} ({}) on {}.".format(nick, mapping.get(level, "Unknown"), level, context.channel)
    except IndexError:
        return "Please provide a nick argument.", Notice(context.nick)


@request('USERLIST')
def userlist_request(bot, context, channel):
    return [x[1] for x in context.session.get({}) if x[0].lower() == channel.lower()]


@request('USERLEVEL')
def userlevel_request(bot, context, channel, nick, host=None):
    userlevel_data = context.session.get({})
    level = IRCLevel.user
    if bot.request('IS_MASTER', nick, host):
        level = IRCLevel.master
    elif channel.lower() == bot.nick.lower():
        level = IRCLevel.owner
    else:
        for c, n in userlevel_data:
            if c.lower() == channel.lower() and n.lower() == nick.lower():
                level = max(userlevel_data[(c, n)])
                break
    return level


@hook('353')
def handle_names(bot, context, message):
    """ Parse the name command and record the userlevels of users. """
    channel = message.params[2]
    names = message.params[-1].split(' ')
    for name in names:
        handle_name(context.session, channel, name)


def handle_name(session, channel, name):
    """ Handle a single name from the name command. """
    userlevels, nick = get_userlevels(name)
    userlevel_data = session.get({})
    userlevel_data[(channel, nick)] = userlevels
    session.set(userlevel_data)


def get_userlevels(name):
    """ Get the userlevel from a nick and return the userlevel and nick. """
    mapping = {
        '+': IRCLevel.voice,
        '%': IRCLevel.hop,
        '@': IRCLevel.aop,
        '&': IRCLevel.sop,
        '~': IRCLevel.owner
    }
    userlevels = [IRCLevel.user]

    for i, c in enumerate(name):
        if c in mapping:
            userlevels.append(mapping[c])
        else:
            return userlevels, name[i:]


@hook('JOIN')
def handle_join(bot, context, message):
    """ Handle the join of a user. """
    channel = message.params[0]
    userlevel_data = context.session.get({})
    userlevel_data[(channel, message.nick)] = [IRCLevel.user]
    context.session.set(userlevel_data)


@hook('NICK')
def handle_nick(bot, context, message):
    """ Handle the nick change of a user. """
    old_nick = message.nick
    new_nick = message.params[0]

    userlevel_data = context.session.get({})
    changes = []
    for channel, nick in userlevel_data:
        if nick == old_nick:
            old = (channel, old_nick)
            new = (channel, new_nick)
            changes.append((old, new))
    for old, new in changes:
        userlevel_data[new] = userlevel_data.pop(old, [IRCLevel.user])
    context.session.set(userlevel_data)


@hook('MODE')
def handle_mode(bot, context, message):
    """ Handle the mode command and update userlevels accordingly. """
    mapping = {
        'v': IRCLevel.voice,
        'h': IRCLevel.hop,
        'o': IRCLevel.aop,
        'a': IRCLevel.sop,
        'q': IRCLevel.owner
    }
    channel = message.params[0]
    nicks = message.params[2:]
    add = True if message.params[1][0] == '+' else False
    modes = message.params[1][1:]

    userlevel_data = context.session.get({})
    for nick, mode in zip(nicks, modes):
        if mode in mapping:
            level = mapping[mode]
            userlevels = userlevel_data[(channel, nick)]
            if add:
                userlevels.append(level)
            else:
                userlevels = [x for x in userlevels if x != level]
            userlevel_data[(channel, nick)] = userlevels
    context.session.set(userlevel_data)


@hook('PART')
def handle_part(bot, context, message):
    """ Handle the part of a user. """
    channel = message.params[0]
    userlevel_data = context.session.get({})
    userlevel_data.pop((channel, message.nick))
    context.session.set(userlevel_data)


@hook('KICK')
def handle_kick(bot, context, message):
    """ Handle the kick of a user. """
    channel = message.params[0]
    nick = message.params[1]
    userlevel_data = context.session.get({})
    userlevel_data.pop((channel, nick))
    context.session.set(userlevel_data)


@hook('QUIT')
def handle_quit(bot, context, message):
    """ Handle the quit of a user. """
    remove = []
    userlevel_data = context.session.get({})
    for channel, nick in userlevel_data:
        if nick == message.nick:
            remove.append((channel, nick))
    for pair in remove:
        userlevel_data.pop(pair)
    context.session.set(userlevel_data)
