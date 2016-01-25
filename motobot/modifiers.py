class Modifier:

    """ Modifier class base, modifies a plugin return message. """

    def modify(self, command, params, trailing):
        """ Override to modify the given parameters.

        Should return command, params, trailing after modification.
        """
        raise NotImplementedError('Should be implemented in derived class.')

    def __call__(self, command, params, trailing):
        return self.modify(command, params, trailing)


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
        command = self.command
        params = params if self.params is None else self.params
        return command, params, trailing


class EatModifier:

    """ Simple empty class for eating plugins. """

    pass


Eat = EatModifier()
