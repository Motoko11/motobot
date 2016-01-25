from motobot import command, sink, Command
from random import choice
import re


@sink()
def regex_sink(bot, database, nick, channel, message):
    for pattern, response in get_patterns(database):
        if pattern.search(message):
            return parse_response(response, nick)


def parse_response(response, nick):
    response = choice(response.split('|'))
    return response.replace('{nick}', nick)


@command('re')
def regex_command(bot, database, nick, channel, message, args):
    arg = args[1].lower()
    if arg == 'add':
        add_regex(' '.join(args[2:]), database)
        response = "Pattern added successfully."
    elif arg == 'del':
        response = rem_regex(' '.join(args[2:]), database)
    elif arg == 'show':
        response = show_patterns(database, nick)
    else:
        response = "Unrecognised argument."

    return response


parse_pattern = re.compile(r'^(.*?)(?: ?)<=>(?: ?)(.*)')


def add_regex(string, database):
    pattern, response = parse_pattern.match(string).groups()

    patterns = get_patterns(database)
    patterns.append((re.compile(pattern, re.IGNORECASE), response))
    save_patterns(database, patterns)


def rem_regex(string, database):
    removed = False
    patterns = get_patterns(database)
    for pattern, response in patterns:
        if pattern.search(string):
            patterns.remove((pattern, response))
            save_patterns(database, patterns)
            return "Pattern matching the string have been removed."
    return "No patterns matched the string."


def show_patterns(database, nick):
    patterns = get_patterns(database)
    responses = []
    modifier = Command('NOTICE', [nick])

    for pattern, response in patterns:
        app = "{}: {};".format(pattern.pattern, response)
        responses.append((app, modifier))
    return responses


patterns_key = 'patterns'
patterns_cache = None


def get_patterns(database):
    global patterns_cache
    if patterns_cache is None:
        patterns_cache = [(re.compile(x, re.I), y) \
            for x, y in database.get_val(patterns_key, [])]
    return patterns_cache


def save_patterns(database, patterns):
    global patterns_cache
    patterns_cache = patterns
    database.set_val(patterns_key, [(x.pattern, y) for x, y in patterns])
