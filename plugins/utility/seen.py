from motobot import command, hook, sink, Priority
from time import strftime, localtime


@command('seen')
def seen_command(bot, context, message, args):
    response = None
    try:
        query = args[1].lower()
        if query == bot.nick.lower():
            response = "I have never seen myself; it's too dark in {}'s slave labour camp.".format(context.channel)
        else:
            response = context.database.get({})[(context.channel, query)]
    except IndexError:
        response = "I see you!"
    except KeyError:
        response = "I've never seen {}.".format(args[1])
    return response


@sink(priority=Priority.max)
def seen_sink(bot, context, message):
    msg = "{} was last seen on {} saying \"{}\".".format(
        context.nick, get_time(), message)
    data = context.database.get({})
    data[(context.channel, context.nick.lower())] = msg
    context.database.set(data)


@hook('JOIN')
def join_hook(bot, context, message):
    msg = "{} was last seen on {} joining the channel.".format(
        message.nick, get_time())
    data = context.database.get({})
    data[(message.params[0], message.nick.lower())] = msg
    context.database.set(data)


@hook('NICK')
def nick_hook(bot, context, message):
    data = context.database.get({})

    msg = "{} was last seen on {} when they changed their nick to {}.".format(
        message.nick, get_time(), message.params[0])
    for key, val in data.items():
        if key[1] == message.nick.lower():
            data[key] = msg

    msg = "{} was last seen on {} when they changed their nick from {}.".format(
        message.params[0], get_time(), message.nick)
    for key, val in data.items():
        if key[1] == message.params[0].lower():
            data[key] = msg

    context.database.set(data)


@hook('QUIT')
def quit_hook(bot, context, message):
    msg = "{} was last seen on {} when they quit.".format(
        message.nick, get_time())
    data = context.database.get({})
    for key, val in data.items():
        if key[1] == message.nick.lower():
            data[key] = msg
    context.database.set(data)


@hook('PART')
def part_hook(bot, context, message):
    msg = "{} was last seen on {} when they part the channel.".format(
        message.nick, get_time())
    data = context.database.get({})
    data[(message.params[0], message.nick.lower())] = msg
    context.database.set(data)


def get_time():
    return strftime('%a %b %d %H:%M:%S', localtime())
