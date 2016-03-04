from motobot import match, Notice, Eat, Priority, __VERSION__
from time import strftime, localtime


@match(r'\x01(.+)\x01', priority=Priority.max)
def ctcp_match(bot, context, message, match):
    ctcp_response = {
        'VERSION': 'MotoBot Version ' + __VERSION__,
        'FINGER': 'Oh you dirty man!',
        'TIME': strftime('%a %b %d %H:%M:%S', localtime()),
        'PING': message
    }
    try:
        ctcp_req = match.group(1)
        reply = ctcp_response[ctcp_req]
        return reply, Notice(context.nick), Eat
    except KeyError:
        return None
