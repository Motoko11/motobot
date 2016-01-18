from motobot import command, IRCLevel


@command('ignore', IRCLevel.op)
def ignore_command(bot, nick, channel, message, args):
    try:
        nick = args[1]
        bot.ignore('{}!*@*'.format(nick))
        return "I am now ignoring {}.".format(nick)
    except IndexError:
        return "Must supply nick to ignore."


@command('ignorehost', IRCLevel.op)
def ignorehost_command(bot, nick, channel, message, args):
    try:
        mask = args[1]
        bot.ignore(mask)
        return "I am now ignoring the mask '{}'.".format(mask)
    except IndexError:
        return "Must supply host to ignore."


@command('unignore', IRCLevel.op)
def unignore_command(bot, nick, channel, message, args):
    try:
        nick = args[1]
        if bot.unignore('{}!*@*'.format(nick)):
            return "I am no longer ignoring {}.".format(nick)
        else:
            return "I wasn't ignoring {}.".format(nick)
    except IndexError:
        return "Must supply nick to unignore."
