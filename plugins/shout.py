from motobot import command


@command('shout')
def shout_command(message):
    return ' '.join(message.message.split(' ')[1:]).upper()
