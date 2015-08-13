from desubot import bot


@bot.command('shout')
def shout_command(message):
    return ' '.join(message.message.split(' ')[1:]).upper()
