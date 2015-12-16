from motobot import command, sink
from random import choice
import re


patterns_key = "re_patterns"


@sink
def regex_sink(bot, message, database):
    for pattern, response in get_patterns(database):
        if pattern.search(message.message):
            return parse_response(response, message)


def parse_response(response, message):
    response = choice(response.split('|'))
    return response.replace('{nick}', message.nick)


@command('re')
def regex_command(bot, message, database):
    args = message.message.split(' ')

    arg = args[1].lower()
    if arg == 'add':
        add_regex(' '.join(args[2:]), database)
        response = "Pattern added successfully."
    elif arg == 'del':
        response = rem_regex(' '.join(args[2:]), database)
    else:
        response = "Unrecognised argument."

    return response


def add_regex(string, database):
    parse_pattern = re.compile(r'^(.*?)(?: ?)<=>(?: ?)(.*)')
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
