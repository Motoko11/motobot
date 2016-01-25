from motobot import hook, command, Command
from time import sleep


@command('join')
def join_command(bot, database, nick, channel, message, args):
    try:
        channel = args[1]
        bot.channels.append(channel)
        return Command('JOIN', channel)
    except IndexError:
        return "Please provide a channel."


@hook('KICK')
def kick_hook(bot, message):
    nick = message.params[1]
    if nick == bot.nick:
        sleep(1)
        channel = message.params[0]
        bot.send('JOIN ' + channel)
