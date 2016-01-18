from motobot import hook
from time import sleep


@hook('PING')
def __handle_ping(bot, message):
    """ Handle the server's pings. """
    bot.send('PONG :' + message.params[-1])


@hook('NOTICE')
def __handle_notice(bot, message):
    """ Use the notice message to identify and register to the server. """
    if not bot.identified:
        bot.send('USER MotoBot localhost localhost MotoBot')
        bot.send('NICK ' + bot.nick)
        sleep(2)

        if bot.nickserv_password is not None:
            bot.send('PRIVMSG nickserv :identify ' + bot.nickserv_password)
            sleep(2)
        for channel in bot.channels:
            bot.send('JOIN ' + channel)
        bot.identified = True


@hook('INVITE')
def __handle_invite(bot, message):
    """ Join a channel when invited. """
    bot.join(message.params[-1])


@hook('ERROR')
def __handle_error(bot, message):
    """ Handle an error message from the server. """
    bot.connected = bot.identified = False
