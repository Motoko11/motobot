from motobot import match
from random import choice

@match(r'^desubot(.+)\?')
def question_match(message, database):
    responses = ['Yes', 'No', 'Hell yea!', 'Are you crazy!?', 'Never',
        'Of course!','It is certain', 'It is decidedly so', 'Without a doubt',
        'Yes definitely', 'You may rely on it', 'As I see it, yes',
        'Most likely', 'Outlook good', 'Signs point to yes', 'Ask again later',
        'Better not tell you now', 'Cannot predict now',
        'Concentrate and ask again', 'Don\'t count on it', 'My reply is no',
        'My sources say no', 'Outlook not so good', 'Very doubtful']
    return choice(responses)
