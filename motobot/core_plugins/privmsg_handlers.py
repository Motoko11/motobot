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
    nick = get_nick(message.sender)
    channel = message.params[0]
    message = strip_control_codes(message.params[-1])

    print("PRIVMSG: {} {} {}".format(nick, channel, message))

    


def strip_control_codes(input):
    """ Strip the control codes from the input. """
    pattern = re.compile(r'\x03[0-9]{0,2},?[0-9]{0,2}|\x02|\x1D|\x1F|\x16|\x0F')
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
