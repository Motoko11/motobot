from motobot import command
from requests import get


def google_search(term):
    pass


@command('g')
@command('google')
def google_command(message, database):
    args = message.message.split(' ')

    if len(args) <= 1:
        return "No search term specified."
    else:
        return google_search(' '.join(args[1:]))
