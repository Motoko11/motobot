from motobot import command, match, IRCLevel
from random import uniform, normalvariate


desu_key = 'desu_plugin_data'


def generate_spam(str):
    """ The needless variables are for later, when stats are added. """
    un = uniform(0, 1) < 0.01
    number = int(round(normalvariate(10, 3)))
    string = 'un' + str if un else str * number
    return un, number, string


@match(r'^desu( *)$')
def desu_match(message, database):
    un, number, string = generate_spam('desu')
    update_stats(database, message.nick, un, number)
    return string


@match(r'^baka( *)$', IRCLevel.op)
def baka_match(message, database):
    un, number, string = generate_spam('baka')
    return string


@match(r'^nya(a+)?n*?(\W|$)')
def nyan_match(message, database):
    num = int(round(normalvariate(15, 3)))
    return 'Ny' + 'a' * num + '~'


@command('desu')
@command('desustats')
def desu_command(message, database):
    args = message.message.split(' ')
    if len(args) <= 1:
        stats = database.get_val(desu_key, {})
        scores = sorted(
            [(x[0], x[1][1]) for x in stats.items()],
            key=lambda item: item[1],
            reverse=True
        )

        response = "Users with most desus: "
        for nick, score in scores[0:5]:
            response += "{} ({}); ".format(nick, score)
        return response

    else:
        nick = ' '.join(args[1:]).rstrip()
        stats = database.get_val(desu_key, {}).get(nick)
        if stats == None:
            return "I have no desu stats for {}.".format(nick)
        else:
            return "{} has desu'd {} times and gotten {} desus, " \
                   "with an average of {} desus. " \
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
