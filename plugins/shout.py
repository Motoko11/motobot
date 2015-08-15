from motobot import command


@command('shout')
def shout_command(message, database):
    return ' '.join(message.message.split(' ')[1:]).upper()
