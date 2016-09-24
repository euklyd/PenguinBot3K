"""
    Plugin Name : Tournament
    Plugin Version : 0.1

    Description:
        Provides basic utility commands, e.g., coin flips.

    Contributors:
        - Popguin / Euklyd

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *
import logging
import random

logger = logging.getLogger(__name__)


class Tournament(Plugin):
    def activate(self):
        random.seed()
        marshu = "http://www.marshu.com/articles/images-website/articles/presidents-on-coins/"  # noqa E501
        self.coins = {"heads": [marshu+"penny-cent-coin-head-thumb.jpg",
                                marshu+"nickel-head-coin-thumb.jpg",
                                marshu+"dime-coin-head-thumb.jpg",
                                marshu+"quarter-coin-head-thumb.jpg",
                                marshu+"half-dollar-coin-head-thumb.jpg"],
                      "tails": [marshu+"penny-cent-coin-tail-thumb.jpg",
                                marshu+"nickel-coin-tail-thumb.jpg",
                                marshu+"dime-coin-tail-thumb.jpg",
                                marshu+"quarter-coin-tail-thumb.jpg",
                                marshu+"half-dollar-coin-tail-thumb.jpg"]
                      }
        pass

    @command("^flip", access=-1)
    def flip(self, msg):
        """`flip`: Flips a coin that will come up either heads or tails. Images of many types of coins are included."""
        coin = random.randint(0, 10)
        if (coin % 2 == 0):
            self.say(msg.channel, self.coins["heads"][int(coin/5)])
        else:
            tails = random.randint(0, 10)
            if (tails % 10 == 0):
                self.say(msg.channel, "https://puu.sh/rlzdJ/c9489a02b4.png")
            else:
                self.say(msg.channel, self.coins["tails"][int(coin/5)])

    @command("^flip-text", access=-1)
    def flip_text(self, msg):
        """`flip-text`: Flips a coin that will come up either heads or tails. Result will be plain text, no images."""
        coin = random.randint(0, 1)
        if (coin % 2 == 0):
            self.say(msg.channel, "<@!{}> flipped a coin and it came up **heads**!".format(msg.sender))
        else:
            self.say(msg.channel, "<@!{}> flipped a coin and it came up **tails**!".format(msg.sender))

    @command("^pick-one (.*)", access=-1)
    def pick_one(self, msg):
        """`pick-one <list of items>`: Selects one item out of a list of space-separated items."""
        args = msg.arguments[0]
        items = args.split(' ')
        choice = random.choice(items)
        self.say(msg.channel, "<@!{}>, your selection is **{}**!".format(msg.sender, choice))

    # def fake_func(self):
    #     print("don't call this lol")
