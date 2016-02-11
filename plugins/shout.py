from motobot import command


@command('shout')
def shout_command(bot, database, context, message, args):
    """ Shout something! """
    return ' '.join(args[1:]).upper()
