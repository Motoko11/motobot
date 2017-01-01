from motobot import match, Notice, Eat, Priority, __VERSION__
from time import strftime, gmtime


@match(r'\x01(.+)\x01', priority=Priority.max)
def ctcp_match(bot, context, message, match):
    ctcp_response = {
        'VERSION': 'MotoBot Version ' + __VERSION__,
        'FINGER': 'Oh you dirty man!',
        'TIME': strftime('%a %b %d %H:%M:%S UTC', gmtime()),
        'PING': message.strip('\x01')
    }
    try:
        ctcp_req = match.group(1).split(' ', 1)[0]
        reply = ctcp_response[ctcp_req]
        response = ('\x01{}\x01'.format(reply), Notice(context.nick), Eat)
    except KeyError:
        response = None
    return response
