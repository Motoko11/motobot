class IRCLevel:
    """ Enum class (Not really) for userlevels. """
    user = 0
    voice = 1
    hop = 2
    op = 3
    aop = 4
    sop = 5


def get_userlevels(nick):
    """ Return the userlevels in a list from a nick. """
    mapping = {
        '+': IRCLevel.voice,
        '%': IRCLevel.hop,
        '@': IRCLevel.op,
        '&': IRCLevel.aop,
        '~': IRCLevel.sop
    }
    levels = [0]
    
    for c in nick:
        level = mapping.get(c, IRCLevel.user)
        if level > 0:
            levels.append(level)
    return levels
