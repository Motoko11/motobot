from motobot import command
from re import compile, IGNORECASE


sed_pattern = compile(r'^(?:.+)sed(?: ?)(?:s?)\/(.*?)\/(.*?)\/(?:.*?) (.+)$', IGNORECASE)


@command('sed')
def sed_command(bot, context, message, args):
    match = sed_pattern.match(message)
    if match is not None:
        pattern, replace, arg = match.groups()
        pattern = compile(pattern, IGNORECASE)
        return pattern.sub(replace, arg)
