class IRCMessage:

    """ Class to store and parse an IRC Message. """

    def __init__(self, msg):
        """ Parse a raw IRC message to IRCMessage. """
        self.sender = None
        self.nick = None
        self.command = None
        self.params = []

        self.__parse_msg(msg)

    def __parse_msg(self, msg):
        if msg[0] == ':':
            self.sender, msg = msg[1:].split(' ', 1)
            self.nick = get_nick(self.sender)

        if ' :' in msg:
            msg, trailing = msg.split(' :', 1)
            self.params = msg.split(' ')
            self.params.append(trailing)
        else:
            self.params = msg.split(' ')
        self.command = self.params.pop(0)

    def __repr__(self):
        """ Print the IRCMessage all nice 'n' pretty. """
        return "Sender: {};\nCommand: {};\nParams: {};\n".format(
            self.sender, self.command, self.params)


def action(message):
    """ Make the message an action. """
    return '\u0001ACTION {}\u0001'.format(message)


def get_nick(host):
    """ Get the user's nick from a host. """
    return host.split('!', 1)[0]
