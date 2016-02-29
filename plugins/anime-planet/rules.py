from motobot import command
from re import compile, IGNORECASE


punctuation = r'.!?;\b'
remove_pants = compile(r'([{0}])[a-z ]*?pant[a-z ]*?[{0}]'.format(punctuation), IGNORECASE)


@command('welcome')
def welcome_command(bot, context, message, args):
    """ Welcome a user to anime-planet.com and read them the rules. """
    response = bot.request('TOPIC', context.channel)
    response = "Welcome to {}!".format(context.channel) \
        if response is None else remove_pants.sub(r'\1', response)
    response = response if len(args) < 2 \
        else "{}: {}".format(' '.join(args[1:]), response)
    return response


@command('stats')
def stats_command(bot, context, message, args):
    """ Return the stats link for #anime-planet.com. """
    if context.channel.lower() == '#anime-planet.com':
        stats_url = 'https://www.chalamius.se/stats/ap.html'
        return "Channel Stats: {}".format(stats_url)


@command('rr')
def rr_command(bot, context, message, args):
    """ Return the recommendations response. Takes single arg for target. """
    response = "If you are looking for anime/manga recommendations we have a database created specifically for that! Just visit www.anime-planet.com and let us do the hard work for you! For channel rules, please go to http://bit.ly/1L1tnfV"

    if len(args) > 1:
        response = "{}: {}".format(' '.join(args[1:]), response)

    return response


@command('mib')
def mib_command(bot, context, message, args):
    """ Help mibs get a real nick. Takes single arg for target. """
    response = "To change your nick to something you'd like type: /nick new_name; If you like that name and it is unregistered. To register it use: /ns REGISTER password [email]; More information can be found here: https://wiki.rizon.net/index.php?title=Register_your_nickname;"

    if len(args) > 1:
        response = "{}: {}".format(' '.join(args[1:]), response)

    return response


@command('worstcharacterofalltime')
def sothis_wishes(bot, context, message, args):
    """ Return the worse character of all time. So says sothis. """
    url = 'http://www.anime-planet.com/characters/makoto-itou'
    return "Behold, the worst anime character of all time, Makoto Itou! {}".format(url)
