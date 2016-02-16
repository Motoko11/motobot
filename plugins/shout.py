from motobot import command


@command('shout')
def shout_command(bot, context, message, args):
    """ Shout something! """
    return ' '.join(args[1:]).upper()
