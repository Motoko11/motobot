from motobot import command, Action, Target, IRCLevel


@command('say', level=IRCLevel.master)
def say_command(bot, database, nick, channel, message, args):
    try:
        target = Target(args[1])
        msg = ' '.join(args[2:])

        if msg.startswith('/me '):
            return msg[4:], target, Action
        else:
            return msg, target

    except IndexError:
        return "You must specify both a channel and a message"
