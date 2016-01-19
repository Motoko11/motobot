from motobot import command


@command('channels')
def channels_command(bot, nick, channel, message, args):
    return '{}'.format(bot.channels)
