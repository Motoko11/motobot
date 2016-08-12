from motobot import hook
from time import sleep


@hook('PING')
def handle_ping(bot, context, message):
    """ Handle the server's pings. """
    bot.send('PONG :' + message.params[-1])


@hook('439')
def handle_wait(bot, context, message):
    """ Handles too fast for server message and waits 1 second. """
    bot.identified = False
    sleep(1)


@hook('NOTICE')
def handle_identification(bot, context, message):
    """ Use the notice message to identify and register to the server. """
    if not bot.identified:
        user = getattr(bot, 'user', 'MotoBot')
        bot.send('USER {0} localhost localhost {0}'.format(user))
        bot.send('NICK ' + bot.nick)
        bot.identified = True


@hook('002')
def handle_nickserv_identification(bot, context, message):
    """ At server welcome message 004 identify to nickserv and join channels. """
    if bot.nickserv_password is not None:
        bot.send('PRIVMSG nickserv :identify ' + bot.nickserv_password)
        sleep(1)


@hook('ERROR')
def handle_error(bot, context, message):
    """ Handle an error message from the server. """
    bot.connected = bot.identified = False
