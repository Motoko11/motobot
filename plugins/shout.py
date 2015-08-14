from motobot import IRCBot


@IRCBot.command('shout')
def shout_command(message):
    return ' '.join(message.message.split(' ')[1:]).upper()
