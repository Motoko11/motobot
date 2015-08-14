from motobot import command, sink
import re


patterns = []


@sink
def regex_sink(message):
    for pattern, response in patterns:
        if pattern.search(message.message):
            return response


@command('re')
def regex_command(message):
    args = message.message.split(' ')

    arg = args[1].lower()
    if arg == 'add':
        add_regex(' '.join(args[2:]))
        response = "Pattern added successfully."
    elif arg == 'del':
        del_regex(' '.join(args[2:]))
        response = "The pattern matching this string has been removed."
    else:
        response = "Unrecognised argument."

    return response


def add_regex(string):
    parse_pattern = re.compile(r'^(.*?)(?: ?)<=>(?: ?)(.*)')
    test = parse_pattern.match(string).groups()
    print(test)


def rem_regex(string):
    for pattern, response in patterns:
        if pattern.search(message.message):
            patterns.pop((pattern, response))
