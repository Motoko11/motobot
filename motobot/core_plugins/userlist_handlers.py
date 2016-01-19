from motobot import hook, IRCLevel, command
from .privmsg_handlers import get_nick


@command('levelprobe')
def levelprobe_command(bot, nick, channel, message, args):
    try:
        mapping = {
            IRCLevel.user: 'has nothing',
            IRCLevel.voice: 'has a voice',
            IRCLevel.hop: 'has a half-op',
            IRCLevel.aop: 'has an ops',
            IRCLevel.sop: 'has a protected ops',
            IRCLevel.owner: 'is the owner'
        }
        return "{} {} in this channel.".format(args[1], mapping[max(bot.userlevels[(channel, args[1])])])
    except IndexError:
        return "Please supply a valid user to probe."
    except KeyError:
        return "Please supply a user who is actually in this channel."


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
    nick = get_nick(message.sender)
    channel = message.params[0]
    bot.userlevels[(channel, nick)] = [IRCLevel.user]


@hook('NICK')
def handle_nick(bot, message):
    """ Handle the nick change of a user. """
    old_nick = get_nick(message.sender)
    new_nick = message.params[0]

    for channel, nick in bot.userlevels:
        if nick == old_nick:
            bot.userlevels[(channel, new_nick)] = \
                bot.userlevels.pop((channel, nick))


@hook('MODE')
def handle_mode(bot, message):
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
def handle_part(bot, message):
    """ Handle the part of a user. """
    nick = get_nick(message.sender)
    channel = message.params[0]
    bot.userlevels.pop((channel, nick))


@hook('KICK')
def handle_kick(bot, message):
    """ Handle the kick of a user. """
    nick = message.params[1]
    channel = message.params[0]
    bot.userlevels.pop((channel, nick))


@hook('QUIT')
def handle_quit(bot, message):
    """ Handle the quit of a user. """
    quitting_nick = get_nick(message.sender)

    for channel, nick in bot.userlevels:
        if nick == quitting_nick:
            bot.userlevels.pop((channel, nick))
