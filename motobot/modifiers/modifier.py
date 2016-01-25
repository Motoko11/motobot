class Modifier:

    """ Modifier class base, modifies a plugin return message. """

    def modify(self, command, params, trailing):
        """ Override to modify the given parameters.

        Should return command, params, trailing after modification.
        """
        raise NotImplementedError('Should be implemented in derived class.')

    def __call__(self, command, params, trailing):
        return self.modify(command, params, trailing)
