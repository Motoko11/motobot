from motobot import command


@command('channels')
def channels_command(bot, message, database):
    return '{}'.format(bot.channels)
