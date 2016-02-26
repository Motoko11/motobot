from collections import namedtuple


Context = namedtuple('Context', 'nick channel database session')


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


def get_userlevel(userlist, nick):
    return next(filter(lambda x: x[0].lower() == nick.lower(), userlist))[1]
