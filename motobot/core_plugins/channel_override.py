from motobot import command, IRCLevel, Priority, Notice


@command('channel', level=IRCLevel.master, priority=Priority.max)
def channel_command(bot, context, message, args):
    """ Override the channel to make a command act as if it were in another channel. """
    try:
        channel = args[1]
        message = ' '.join(args[2:])
        return bot.request('HANDLE_MESSAGE', context.nick, channel, context.host, message)
    except IndexError:
        return "Error: Please provide a channel.", Notice(context.nick)
