from motobot import hook, request


@request('TOPIC')
def topic_request(bot, context, channel):
    return context.session.get({}).get(channel.lower(), None)


@hook('332')
def handle_topic(bot, context, message):
    channel = message.params[1].lower()
    topic = message.params[-1]
    topics = context.session.get({})
    topics[channel] = topic
    context.session.set(topics)
