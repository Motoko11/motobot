from motobot import IRCBot, hook, Priority
from time import strftime, localtime
import re


@hook('PRIVMSG')
def handle_privmsg(bot, message):
    """ Handle the privmsg commands.

    Will send messages to each plugin accounting for priority and level.

    """
    nick = get_nick(message.sender)
    channel = message.params[0]
    message = strip_control_codes(message.params[-1])

    break_priority = Priority.min
    for plugin in bot.plugins:
        if break_priority > plugin[2]:
            break
        else:
            responses = handle_plugin(bot, plugin, nick, channel, message)
            handle_responses(bot, nick, channel, responses)


def handle_plugin(bot, plugin, nick, channel, message):
    # TODO: Manage userlevels
    responses = None

    if plugin[1] == IRCBot.command_plugin:
        responses = handle_command(plugin, bot, nick, channel, message)
    elif plugin[1] == IRCBot.match_plugin:
        responses = handle_match(plugin, bot, nick, channel, message)
    elif plugin[1] == IRCBot.sink_plugin:
        responses = handle_sink(plugin, bot, nick, channel, message)

    return responses


def handle_command(plugin, bot, nick, channel, message):
    trigger = bot.command_prefix + plugin[4]
    test = message.split(' ', 1)[0]
    
    if trigger == test:
        args = message[len(bot.command_prefix):].split(' ')
        return plugin[0](bot, nick, channel, message, args)


def handle_match(plugin, bot, nick, channel, message):
    match = plugin[4].search(message)
    if match is not None:
        return plugin[0](bot, nick, channel, message, match)


def handle_sink(plugin, bot, nick, channel, message):
    return plugin[0](bot, nick, channel, message)


def handle_responses(bot, nick, channel, responses):
    # TODO: This is temporary
    if responses is not None:
        target = channel if channel != bot.nick else nick
        bot.send('PRIVMSG {} :{}'.format(target, responses))


pattern = re.compile(r'\x03[0-9]{0,2},?[0-9]{0,2}|\x02|\x1D|\x1F|\x16|\x0F+')


def strip_control_codes(input):
    """ Strip the control codes from the input. """
    output = pattern.sub('', input)
    return output


def get_nick(host):
    """ Get the user's nick from a host. """
    return host.split('!')[0]


def is_channel(name):
    """ Check if a name is a valid channel name or not. """
    valid = ['&', '#', '+', '!']
    invalid = [' ', ',', '\u0007']
    return (name[0] in valid) and all(c not in invalid for c in name)


def is_ctcp(message):
    """ Check if a message is a ctcp message or not. """
    char_1 = '\u0001'
    return message[0] == char_1 and message[-1] == char_1


def ctcp_response(message):
    """ Return the appropriate response to a CTCP request. """
    mapping = {
        'VERSION': 'MotoBot Version 2.0',
        'FINGER': 'Oh you dirty man!',
        'TIME': strftime('%a %b %d %H:%M:%S', localtime()),
        'PING': message
    }
    return mapping.get(message.split(' ')[0].upper(), None)
