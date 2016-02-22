from motobot import command
from codecs import encode


@command('rot13')
def rot13_command(bot, context, message, args):
    return encode(' '.join(args[1:]), 'rot13')
