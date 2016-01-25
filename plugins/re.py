from motobot import command, sink, Command, Priority, Eat
from random import choice
import re


@sink(priority=Priority.lowest)
def regex_sink(bot, database, nick, channel, message):
    for pattern, response in get_patterns(database):
        if pattern.search(message):
            return parse_response(response, nick)


def parse_response(response, nick):
    response = choice(response.split('|'))
    return response.replace('{nick}', nick)


@command('re', priority=Priority.lower)
def regex_command(bot, database, nick, channel, message, args):
    arg = args[1].lower()
    if arg == 'add':
        response = (add_regex(' '.join(args[2:]), database), Eat)
    elif arg == 'del' or arg == 'rem':
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
    return "Pattern added successfully."


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
    responses = []
    modifier = Command('NOTICE', nick)

    print(get_patterns(database))
    for pattern, response in get_patterns(database):
        app = "{}: {};".format(pattern.pattern, response)
        responses.append((app, modifier))
    return responses


patterns_cache = None


def get_patterns(database):
    global patterns_cache
    if patterns_cache is None:
        patterns_cache = [(re.compile(x, re.I), y) \
            for x, y in database.get_val([])]
    return patterns_cache


def save_patterns(database, patterns):
    global patterns_cache
    patterns_cache = patterns
    database.set_val([(x.pattern, y) for x, y in patterns])
