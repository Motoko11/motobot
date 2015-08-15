from motobot import command, sink
from random import choice
import re


patterns = []


@sink
def regex_sink(message):
    for pattern, response in patterns:
        if pattern.search(message.message):
            return parse_response(response, message)


@command('re')
def regex_command(message):
    args = message.message.split(' ')

    arg = args[1].lower()
    if arg == 'add':
        add_regex(' '.join(args[2:]))
        response = "Pattern added successfully."
    elif arg == 'del':
        response = rem_regex(' '.join(args[2:]))
    else:
        response = "Unrecognised argument."

    return response


def add_regex(string):
    parse_pattern = re.compile(r'^(.*?)(?: ?)<=>(?: ?)(.*)')
    pattern, response = parse_pattern.match(string).groups()
    patterns.append((re.compile(pattern, re.IGNORECASE), response))


def rem_regex(string):
    removed = False
    for pattern, response in patterns:
        if pattern.search(string):
            patterns.remove((pattern, response))
            return "Pattern matching the string have been removed."
    return "No patterns matched the string."


def parse_response(response, message):
    response = choice(response.split('|'))
    return response.replace('{nick}', message.nick)
