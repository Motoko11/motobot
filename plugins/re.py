from motobot import command, sink, Notice, Priority, Eat, Action
from random import choice
from re import compile, IGNORECASE


@sink(priority=Priority.lowest)
def regex_sink(bot, database, nick, channel, message):
    responses = []

    for pattern, response in get_patterns(database):
        if pattern.search(message):
            responses.append(parse_response(response, nick))

    return responses


def parse_response(response, nick):
    response = choice(response.split('|')).replace('{nick}', nick)

    if response.startswith('/me '):
        response = (response[4:], Action)
    return response


@command('re', priority=Priority.lower)
def regex_command(bot, database, nick, channel, message, args):
    """ Manage regex matches on bot.

    Valid arguments are: 'add', 'del', and 'show'.
    'add' usage: re add [pattern] <=> [response];
    'del' usage: re del [pattern];
    'show' usage: re show [pattern];
    If pattern is not specified, a list of triggers will be returned.
    """
    arg = args[1].lower()
    if arg == 'add':
        response = (add_regex(' '.join(args[2:]), database))
    elif arg == 'del' or arg == 'rem':
        response = (rem_regex(' '.join(args[2:]), database))
    elif arg == 'show':
        search = ' '.join(args[2:])
        if search != '':
            response = show_patterns(database, search)
        else:
            response = show_triggers(database)
    else:
        response = "Error: Unrecognised argument."

    return response, Eat, Notice(nick)


parse_pattern = compile(r'^(.+?)(?: ?)<=>(?: ?)(.+)')


def add_regex(string, database):
    pattern, response = parse_pattern.match(string).groups()

    patterns = get_patterns(database)
    patterns.append((compile(pattern, IGNORECASE), response))
    save_patterns(database, patterns)
    return "Pattern added successfully."


def rem_regex(string, database):
    remove = []
    response = "No patterns matched the string."
    patterns = get_patterns(database)

    for pattern, response in patterns:
        if string.lower() == pattern.pattern.lower() or pattern.search(string):
            remove.append((pattern, response))

    for pattern in remove:
        patterns.remove(pattern)

    if remove != []:
        response = "Pattern(s) matching the string have been removed."
        save_patterns(database, patterns)

    return response


def show_patterns(database, arg):
    responses = []

    for pattern, response in get_patterns(database):
        if arg.lower() == pattern.pattern.lower() or pattern.search(arg):
            app = "{}: {};".format(pattern.pattern, response)
            responses.append(app)

    if responses == []:
        responses = "There are no patterns that match the given string."

    return responses


def show_triggers(database):
    triggers = [x[0].pattern for x in get_patterns(database)]
    responses = []
    format_string = "Triggers: {};"
    separator = ", "
    max_length = 425

    while triggers != []:
        cur = []
        length = len(format_string)

        while triggers != []:
            l = len(triggers[0]) + len(separator)
            if length + l <= max_length:
                length += l
                cur.append(triggers.pop(0))
            else:
                break

        msg = format_string.format(separator.join(cur))
        responses.append(msg)

    if responses == []:
        responses = "There are no patterns currently saved."

    return responses


patterns_cache = None


def get_patterns(database):
    global patterns_cache
    if patterns_cache is None:
        patterns_cache = [(compile(x, IGNORECASE), y) \
            for x, y in database.get_val([])]
    return patterns_cache


def save_patterns(database, patterns):
    global patterns_cache
    patterns_cache = patterns
    database.set_val([(x.pattern, y) for x, y in patterns])
