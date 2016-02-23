from motobot import command, sink, Priority, split_response
from collections import defaultdict


lines = defaultdict(lambda: [])


@sink(priority=Priority.high)
def last_sink(bot, context, message):
    global lines
    max_lines = 25
    lines[context.channel].append((context.nick, message))

    while len(lines[context.channel]) > max_lines:
        lines[context.channel].pop(0)


def format_lines(l):
    for nick, msg in l:
        yield "<{}> {}".format(nick, msg)


@command('last', priority=Priority.higher)
def last_command(bot, context, message, args):
    global lines
    response = None

    try:
        n = int(args[1])
        l = lines[context.channel][-n:]
        response = split_response(format_lines(l), separator=' ')
    except (ValueError, IndexError):
        response = ("Error: Must supply integer argument.", Notice(context.nick))

    return response
