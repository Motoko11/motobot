from motobot import command, match, IRCLevel
from random import uniform, randint, choice
from time import time


desu_key = 'desu_plugin_data'
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
def desu_match(bot, nick, channel, message, match):
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

        update_stats(bot.database, nick, un, number)
        return string
    else:
        return "You've desu'd too recently to desu again."


@match(r'^baka( *)$', IRCLevel.op)
def baka_match(bot, nick, channel, message, match):
    return 'baka' * randint(1, 30)


@match(r'^n(a+)?(y+)(a+)(n+)?(\W|$)')
def nyan_match(bot, nick, channel, message, match):
    num = randint(5, 50)
    return 'Ny' + 'a' * num + '~'



@command('desustats')
def desu_command(bot, nick, channel, message, args):
    stats = bot.database.get_val(desu_key, {})
    scores = sorted(
        [(x[0], x[1][1]) for x in stats.items()],
        key=lambda item: item[1],
        reverse=True
    )

    response = "Users with most desus: "
    for nick, score in scores[0:10]:
        response += "{} ({}); ".format(nick, score)
    return response


@command('desu')
def desu_command(bot, nick, channel, message, args):
    nick = ''
    if len(args) <= 1:
        nick = nick
    else:
        nick = ' '.join(args[1:]).rstrip()
    
    stats = bot.database.get_val(desu_key, {}).get(nick)
    if stats == None:
        return "I have no desu stats for {}.".format(nick)
    else:
        return "{} has desu'd {} times and gotten {} desus, " \
               "with an average of {:.2f} desus. " \
               "They have been undesu'd {} times.".format(
                    nick, stats[0], stats[1], stats[1]/ stats[0], stats[2]
                )


def update_stats(database, nick, un, number):
    stats = database.get_val(desu_key, {})
    userstats = stats.get(nick, [0, 0, 0])

    userstats[0] += 1
    if un:
        userstats[2] += 1
    else:
        userstats[1] += number

    stats[nick] = userstats
    database.set_val(desu_key, stats)
