from motobot import hook
from time import strftime, localtime
import re


@hook('PRIVMSG')
def __handle_privmsg(bot, message):
    """ Handle the privmsg commands.

    Will send the reply back to the channel the command was sent from, 
    or back to the user whom sent it in the case of a private message.
    Commands (prefixed with command_prefix) are executed, CTCP is handled,
    and the matches are checked.

    """
    response = None

    message.message = strip_control_codes(message.message)

    target = message.channel \
        if is_channel(message.channel) \
        else message.nick

    if message.message.startswith(bot.command_prefix):
        command = message.message.split(' ')[0][len(bot.command_prefix):]
        response = bot.commands[command](bot, message, bot.database)
        if response is not None:
            response = 'PRIVMSG {} :{}'.format(target, response)

    elif is_ctcp(message):
        response = ctcp_response(message.message[1:-1])
        if response is not None:
            response = 'NOTICE {} :\u0001{}\u0001'.format(target, response)

    else:
        for pattern, func in bot.patterns:
            if pattern.search(message.message):
                response = func(bot, message, bot.database)
                if response is not None:
                    response = 'PRIVMSG {} :{}'.format(target, response)

        if response is None:
            for sink in bot.sinks:
                response = sink(bot, message, bot.database)
                if response is not None:
                    response = 'PRIVMSG {} :{}'.format(target, response)
                    break

    return response


def strip_control_codes(input):
    """ Strip the control codes from the input. """
    pattern = re.compile(r'\x03[0-9]{0,2},?[0-9]{0,2}|\x02|\x1D|\x1F|\x16|\x0F')
    output = pattern.sub('', input)
    return output


def is_channel(name):
    """ Check if a name is a valid channel name or not. """
    valid = ['&', '#', '+', '!']
    invalid = [' ', ',', '\u0007']
    return (name[0] in valid) and all(c not in invalid for c in name)


def is_ctcp(message):
    """ Check if a message object is a ctcp message or not. """
    return message.message.startswith('\u0001') and \
        message.message.endswith('\u0001')


def ctcp_response(message):
    """ Return the appropriate response to a CTCP request. """
    mapping = {
        'VERSION': 'MotoBot Version 2.0',
        'FINGER': 'Oh you dirty man!',
        'TIME': strftime('%a %b %d %H:%M:%S', localtime()),
        'PING': message
    }
    return mapping.get(message.split(' ')[0].upper(), None)
