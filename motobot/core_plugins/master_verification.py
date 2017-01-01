from motobot import hook, request, command


@request('IS_MASTER')
def is_master_request(bot, context, nick):
    confirmed = get_master_lists(bot, context.session)[0]
    return nick.lower() in confirmed
