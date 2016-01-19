from motobot import command, action, IRCLevel


@command('say', level=IRCLevel.master)
def say_command(bot, nick, channel, message, args):
    if len(args) < 3:
        return "You must specify both a channel and a message"
    else:
        channel = args[1]
        message = ' '.join(args[2:])
        if message.startswith('/me '):
            message = action(message[4:])
        bot.send('PRIVMSG {} :{}'.format(channel, message))
