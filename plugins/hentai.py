from motobot import command
from random import choice


#@command('hentai')
def hentai_command(message, database):
    # From: http://imgur.com/gallery/l5N4l
    responses = [
        "Your Penis! I like your dick more than games!",
        "Ahhh, the smell of burning flesh... Smells great!",
        "If I had known how well it would turn out, I would've raped her when she was younger.",
        "But now I'm taking you to a cum-hell where you'll be cumming forever.",
        "After a kiss comes a blowjob, right?",
        "What are you waiting for!? Just hurry up and fuck me!",
        "An elementary school girl with a huge cock, on her way to school. I wonder how much she will grow in the future?",
        "Hafu... Hafu... Doing a bukkake on an elementary school girl gives such a sense of fulfillment!!"
    ]

    return choice(responses)
