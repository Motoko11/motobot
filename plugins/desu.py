from motobot import command, match, IRCLevel, Command, Eat
from random import uniform, randint, choice
from time import time


desu_time_guard = {}


def can_desu(nick):
    last_desus = desu_time_guard.get(nick, [0, 0, 0, 0, 0])
    current_time = time()

    ret = not all(current_time - x <= 5 * 60 for x in last_desus)
    if ret:
        last_desus.pop(0)
        last_desus.append(current_time)
        desu_time_guard[nick] = last_desus
    return ret


@match(r'^desu( *)$')
def desu_match(bot, database, nick, channel, message, match):
    if can_desu(nick):
        chance = uniform(0, 1)
        number = randint(1, 30)
        string = ''
        un = chance <= 0.01

        if un:
            if chance <= 0.01:
                special_desus = ['omgdesu', 'dechu']
                string = choice(special_desus)
            else:
                string = 'undesu'
        else:
            string = 'desu' * number

        update_stats(database, nick, un, number)
        return string
    else:
        return "You've desu'd too recently to desu again."


@match(r'^baka( *)$', level=IRCLevel.op, alt=lambda *x, **xs: Eat)
def baka_match(bot, database, nick, channel, message, match):
    return 'baka' * randint(1, 30)


@match(r'^n(a+)?(y+)(a+)(n+)?(\W|$)')
def nyan_match(bot, database, nick, channel, message, match):
    num = randint(5, 50)
    return 'Ny' + 'a' * num + '~'


@command('desu')
def desu_command(bot, database, nick, channel, message, args):
    """ Return desu stats of the queried user.

    If an argument is given, queries for stats from that user.
    If no argument is given, queries for stats from the requesting user.
    """
    try:
        return user_stats(database, args[1])
    except IndexError:
        return user_stats(database, nick)


def user_stats(database, nick):
    stats = database.get_val({})
    userstats = stats.get(nick)
    if userstats == None:
        return "I have no desu stats for {}.".format(nick)
    else:
        return "{} has desu'd {} times and gotten {} desus, " \
               "with an average of {:.2f} desus. " \
               "They have been undesu'd {} times.".format(
                    nick, userstats[0], userstats[1],
                    userstats[1]/ userstats[0], userstats[2]
                )


@command('topdesu')
@command('desustats')
def top_desu_command(bot, database, nick, channel, message, args):
    """ Return the users with the highest desu score for the given argument.

    Valid arguments are: 'number', 'average', and 'undesus'.
    The default argument is 'number'.
    """
    keys = {
        'number': lambda x: x[1][1],
        'average': lambda x: x[1][1] / x[1][0],
        'undesus': lambda x: x[1][2]
    }
    response = ''
    modifier = Command('NOTICE', nick)

    try:
        stats = database.get_val({})
        arg = args[1].lower() if len(args) > 1 else 'number'
        key = keys[arg]

        response = "Users with the highest score desus ({}): ".format(arg)
        for stats in sorted(stats.items(), reverse=True, key=key)[:10]:
            response += "{}: {}; ".format(stats[0], key(stats))

    except KeyError:
        response = "Invalid argument, valid arguments are: " + \
            ", ".join(keys.keys()) + '.'

    return response, modifier


def update_stats(database, nick, un, number):
    stats = database.get_val({})
    userstats = stats.get(nick, [0, 0, 0])

    userstats[0] += 1
    if un:
        userstats[2] += 1
    else:
        userstats[1] += number

    stats[nick] = userstats
    database.set_val(stats)
