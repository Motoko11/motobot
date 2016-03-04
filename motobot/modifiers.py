class Modifier:

    """ Modifier class base. """

    require_trailing = True


class CommandModifier(Modifier):
    def modify_command(self, command):
        raise NotImplementedError


class ParamsModifier(Modifier):
    def modify_params(self, params):
        raise NotImplementedError


class TrailingModifier(Modifier):
    def modify_trailing(self, trailing):
        raise NotImplementedError


class EatType(Modifier):

    """ Simple empty class for eating plugins. """

    pass


Eat = EatType()


class ActionType(TrailingModifier):

    """ Modifier class to turn a message into an action. """

    def modify_trailing(self, trailing):
        return '\x01ACTION {}\x01'.format(trailing)


Action = ActionType()


class CTCPType(TrailingModifier):

    """ Modifier class to turn a message into a CTCP message. """

    def modify_trailing(self, trailing):
        return '\x01{}\x01'.format(trailing)


CTCP = CTCPType()


class Target(ParamsModifier):

    """ Modifier class to change the target of a message. """

    def __init__(self, target):
        self.target = target

    def modify_params(self, params):
        return [self.target]


class Command(CommandModifier, ParamsModifier):

    """ Modifier class to override the command, and optionally the params of a message. """

    require_trailing = False

    def __init__(self, command, params=None):
        self.command = command
        self.params = params if not isinstance(params, str) else [params]

    def modify_command(self, command):
        return self.command

    def modify_params(self, params):
        return params if self.params is None else self.params


def Notice(nick):
    command = Command('NOTICE', nick)
    command.require_trailing = False
    return command
