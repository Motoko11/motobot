from motobot import command, IRCLevel


@command('ignore', IRCLevel.op)
def ignore_command(bot, nick, channel, message, args):
    try:
        nick_arg = args[1]
        bot.ignore('{}!*@*'.format(nick_arg))
        return "I am now ignoring {}.".format(nick_arg)
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
        nick_arg = args[1]
        if bot.unignore('{}!*@*'.format(nick_arg)):
            return "I am no longer ignoring {}.".format(nick_arg)
        else:
            return "I wasn't ignoring {}.".format(nick_arg)
    except IndexError:
        return "Must supply nick to unignore."
