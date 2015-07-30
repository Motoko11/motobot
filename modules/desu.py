from desubot import bot
from random import uniform, normalvariate


def generate_spam(str):
    """ The needless variables are for later, when stats are added. """
    un = uniform(0, 1) < 0.05
    number = int(round(normalvariate(10, 3)))
    string = 'un' + str if un else str * number
    return un, number, string


@bot.match(r'^desu.*')
def desu_match(message):
    un, number, string = generate_spam('desu')
    return string


@bot.match(r'^baka.*')
def baka_match(message):
    if bot.get_userlevel(message.nick, message.channel) >= 3:
        un, number, string = generate_spam('baka')
        return string


@bot.command('desu')
@bot.command('desustats')
def desu_command(message):
    return "Provisional command for desu stats."
