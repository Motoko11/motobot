from motobot import command, match, IRCLevel, Command
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


@match(r'^baka( *)$', IRCLevel.op)
def baka_match(bot, database, nick, channel, message, match):
    return 'baka' * randint(1, 30)


@match(r'^n(a+)?(y+)(a+)(n+)?(\W|$)')
def nyan_match(bot, database, nick, channel, message, match):
    num = randint(5, 50)
    return 'Ny' + 'a' * num + '~'


@command('desu')
def desu_command(bot, database, nick, channel, message, args):
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
def top_desu_command(bot, database, nick, channel, message, args):
    try:
        stats = database.get_val({})
        arg = args[1].lower() if len(args) > 1 else 'number'
        keys = {
            'number': lambda x: x[1][1],
            'average': lambda x: x[1][1] / x[1][0],
            'undesus': lambda x: x[1][2]
        }
        key = keys[arg]

        response = "Users with the highest score desus ({}): ".format(arg)
        for stats in sorted(stats.items(), reverse=True, key=key)[:10]:
            response += "{}: {}; ".format(stats[0], key(stats))

        return response, Command('NOTICE', [nick])
    except KeyError:
        return "Error: Not a valid argument. Valid arguments are: .", Command('NOTICE', [nick])


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
