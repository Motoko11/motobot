import re


class IRCMessage:

    """ Class to store and parse an IRC Message. """

    parse_pattern = re.compile(
        r'^(?:[:](\S+) )?(\S+)(?: (?!:)(.+?))?(?: [:](.+))?$'
    )

    def __init__(self, msg):
        """ Parse a raw IRC message to IRCMessage. """
        match = IRCMessage.parse_pattern.match(msg)
        self.sender, self.command, self.channel, self.message = match.groups()
        self.nick = get_nick(self.sender)

    def __repr__(self):
        """ Print the IRCMessage all nice 'n' pretty. """
        return "Sender: {};\nCommand: {};\nChannel: {};\nMessage: {};".format(
            self.sender, self.command, self.channel, self.message)


def get_nick(host):
    """ Get the user's nick from a host. """
    if host is not None:
        return host.split('!')[0]
