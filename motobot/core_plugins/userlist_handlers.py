from motobot import hook
from ..irc_level import get_userlevels


@hook('353')
def handle_names(bot, message):
    """ Parse the name command and record the userlevels of users. """
    pass


@hook('JOIN')
def handle_join(bot, message):
    """ Handle the join of a user. """
    pass


@hook('MODE')
def handle_mode(bot, message):
    """ Handle the mode command and update userlevels accordingly. """
    pass


@hook('PART')
@hook('QUIT')
def handle_leave(bot, message):
    """ Handle the part or quit of a user. """
    pass
