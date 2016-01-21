from .modifer import Modifier


class ActionModifier(Modifier):

    """ Modifier class to turn a message into an action. """

    def modify(self, command, params, trailing):
        trailing = '\x01ACTION {}\x01'.format(trailing)
        return command, params, trailing


Action = ActionModifier()


class Target(Modifier):

    """ Modifier class to change the target of a message. """

    def __init__(self, target):
        self.target = target

    def modify(self, command, params, trailing):
        params[0] = self.target
        return command, params, trailing


class Command(Modifier):

    """ Modifier class to override the command, and optionally the params of a message. """

    def __init__(self, command, params=None):
        self.command = command
        self.params = params

    def modify(self, command, params, trailing):
        command = command
        params = params if self.params is None else self.params
        return command, params, trailing
