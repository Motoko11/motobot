from motobot import hook
from time import sleep


@hook('PING')
def handle_ping(bot, message):
    """ Handle the server's pings. """
    bot.send('PONG :' + message.params[-1])


@hook('439')
def handle_wait(bot, message):
    """ Handles too fast for server message and waits 1 second. """
    bot.identified = False
    sleep(1)


@hook('NOTICE')
def handle_identification(bot, message):
    """ Use the notice message to identify and register to the server. """
    if not bot.identified:
        bot.send('USER MotoBot localhost localhost MotoBot')
        bot.send('NICK ' + bot.nick)
        bot.identified = True


@hook('004')
def handle_nickserv_identification(bot, message):
    """ At server welcome message 004 identify to nickserv and join channels. """
    if bot.nickserv_password is not None:
        bot.send('PRIVMSG nickserv :identify ' + bot.nickserv_password)
    for channel in bot.channels:
        bot.send('JOIN ' + channel)


@hook('ERROR')
def handle_error(bot, message):
    """ Handle an error message from the server. """
    bot.connected = bot.identified = False
