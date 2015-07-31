from .. import IRCBot
from time import sleep

@IRCBot.message_hook('439')
def identify_hook(bot, message):
    bot.send('USER MotoBot localhost localhost MotoBot')
    sleep(1)
    bot.send('NICK ' + bot.nick)
    # TODO: Actually make a way (Other than inviting) to have the bot join
    bot.send('JOIN #Moto-chan')
    bot.send('JOIN #animu')
    bot.send('JOIN #anime-planet.com')


@IRCBot.message_hook('PING')
def ping_hook(bot, message):
    return 'PONG :' + message.message


@IRCBot.message_hook('ERROR')
def error_hook(bot, message):
    bot.connected = False


@IRCBot.message_hook('INVITE')
def invite_hook(bot, message):
    return 'JOIN ' + message.message


@IRCBot.message_hook('353')
def names_hook(bot, message):
    channel = message.channel.split(' ')[2]

    for name in message.message.split(' '):
        level = get_level(name[0])
        nick = name if level == 0 else name[1:]
        bot.userlist[(channel, nick)] = level


def get_level(symbol):
    mapping = {
        '~': 5,
        '&': 4,
        '@': 3,
        '%': 2,
        '+': 1
    }
    return mapping[symbol] if symbol in mapping else 0


@IRCBot.message_hook('PRIVMSG')
def msg_hook(bot, message):
    response = None
    if message.message.startswith(bot.command_prefix):
        command = message.message.split(' ')[0][1:]
        if command in bot.commands:
            response = bot.commands[command](message)

    else:
        for pattern, func in bot.patterns:
            if pattern.search(message.message):
                response = func(message)

    if response is not None:
        target = message.channel \
            if is_channel(message.channel) else message.nick
        return 'PRIVMSG ' + target + ' :' + response


def is_channel(channel_name):
    """ Ugliest function ever """
    return (channel_name[0] == '#' or
            channel_name[0] == '@' or
            channel_name[0] == '+' or
            channel_name[0] == '!') and \
            ' ' not in channel_name and \
            ',' not in channel_name
