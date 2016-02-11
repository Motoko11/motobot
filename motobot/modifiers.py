class Modifier:

    """ Modifier class base, modifies a plugin return message. """

    def modify_command(self, command):
        return command

    def modify_params(self, params):
        return params

    def modify_trailing(self, trailing):
        return trailing


class ActionModifier(Modifier):

    """ Modifier class to turn a message into an action. """

    def modify_trailing(self, trailing):
        return '\x01ACTION {}\x01'.format(trailing)


Action = ActionModifier()


class CTCPModifier(Modifier):

    """ Modifier class to turn a message into an action. """

    def modify_trailing(self, trailing):
        return '\x01{}\x01'.format(trailing)


CTCP = CTCPModifier()


class Target(Modifier):

    """ Modifier class to change the target of a message. """

    def __init__(self, target):
        self.target = target

    def modify_params(self, params):
        params[0] = self.target
        return params


class Command(Modifier):

    """ Modifier class to override the command, and optionally the params of a message. """

    def __init__(self, command, params=None):
        self.command = command
        self.params = params if not isinstance(params, str) else [params]

    def modify_command(self, command):
        return self.command

    def modify_params(self, params):
        return params if self.params is None else self.params


Notice = lambda nick: Command('NOTICE', nick)


class EatModifier:

    """ Simple empty class for eating plugins. """

    pass


Eat = EatModifier()
