from motobot import hook, IRCLevel


@hook('353')
def handle_names(bot, message):
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

    for i in range(len(name)):
        if name[i] in mapping:
            userlevels.append(mapping[name[i]])
        else:
            return userlevels, name[i:]


@hook('JOIN')
def handle_join(bot, message):
    """ Handle the join of a user. """
    pass


@hook('MODE')
def handle_mode(bot, message):
    """ Handle the mode command and update userlevels accordingly. """
    pass


@hook('PART')
@hook('QUIT')
def handle_leave(bot, message):
    """ Handle the part or quit of a user. """
    pass
