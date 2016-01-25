from motobot import command


@command('shout')
def shout_command(bot, database, nick, channel, message, args):
    return ' '.join(args[1:]).upper()
