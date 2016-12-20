from collections import namedtuple
from re import compile


Context = namedtuple('Context', 'nick channel host database session')


class BotError(Exception):

    """ Exception class for MotoBot plugins. """

    pass


def split_response(iterable, format_string='{}', separator=', ', max_length=400):
    """ Take an iterable and output a messages generator. """
    cur = ''

    for x in iterable:
        if len(cur) + len(format_string) + len(x) >= max_length:
            msg = format_string.format(cur)
            cur = ''
            yield msg
        cur += (separator if cur != '' else '') + x

    if cur != '':
        msg = format_string.format(cur)
        yield msg


pattern = compile(r'\x03[0-9]{0,2},?[0-9]{0,2}|\x02|\x1D|\x1F|\x16|\x0F+')


def strip_control_codes(input):
    """ Strip the control codes from the input. """
    output = pattern.sub('', input)
    return output
