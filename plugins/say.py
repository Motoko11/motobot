from motobot import command, Action, Target, IRCLevel


@command('say', level=IRCLevel.master)
def say_command(bot, nick, channel, message, args):
    try:
        target = Target(args[1])
        msg = ' '.join(args[2:])

        if message.startswith('/me '):
            return msg, target, Action
        else:
            return msg, target

    except IndexError:
        return "You must specify both a channel and a message"
