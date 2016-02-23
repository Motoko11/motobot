from motobot import hook, IRCLevel


@hook('353')
def handle_names(bot, context, message):
    """ Parse the name command and record the userlevels of users. """
    channel = message.params[2]
    names = message.params[-1].split(' ')
    for name in names:
        handle_name(bot, channel, name)


def handle_name(bot, channel, name):
    """ Handle a single name from the name command. """
    userlevels, nick = get_userlevels(name)
    bot.userlevels[(channel, nick)] = userlevels


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
    bot.userlevels[(channel, message.nick)] = [IRCLevel.user]


@hook('NICK')
def handle_nick(bot, context, message):
    """ Handle the nick change of a user. """
    old_nick = message.nick
    new_nick = message.params[0]

    for channel, nick in bot.userlevels:
        if nick == old_nick:
            bot.userlevels[(channel, new_nick)] = \
                bot.userlevels.pop((channel, nick))


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

    for nick, mode in zip(nicks, modes):
        if mode in mapping:
            level = mapping[mode]
            userlevels = bot.userlevels[(channel, nick)]
            if add:
                userlevels.append(level)
            else:
                userlevels = [x for x in userlevels if x != level]
            bot.userlevels[(channel, nick)] = userlevels


@hook('PART')
def handle_part(bot, context, message):
    """ Handle the part of a user. """
    channel = message.params[0]
    bot.userlevels.pop((channel, message.nick))


@hook('KICK')
def handle_kick(bot, context, message):
    """ Handle the kick of a user. """
    nick = message.params[1]
    channel = message.params[0]
    bot.userlevels.pop((channel, nick))


@hook('QUIT')
def handle_quit(bot, context, message):
    """ Handle the quit of a user. """
    remove = []
    for channel, nick in bot.userlevels:
        if nick == message.nick:
            remove.append((channel, nick))
    for pair in remove:
        bot.userlevels.pop(pair)
