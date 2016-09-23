"""
    Plugin Name : Utility
    Plugin Version : 0.1

    Description:
        Provides basic utility commands, e.g., coin flips.

    Contributors:
        - Fulminant Edge / Euklyd

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


class Utility(Plugin):
    def activate(self):
        random.seed()
        marshu = "http://www.marshu.com/articles/images-website/articles/presidents-on-coins/"  # noqa E501
        self.coins = {"heads": [marshu+"penny-cent-coin-head-thumb.jpg",
                                marshu+"nickel-head-coin-thumb.jpg",
                                marshu+"dime-coin-head-thumb.jpg",
                                marshu+"quarter-coin-head-thumb.jpg",
                                marshu+"half-dollar-coin-head-thumb.jpg"],
                      "tails": [marshu+"penny-cent-coin-tail-thumb.jpg",
                                marshu+"nickel-tail-coin-thumb.jpg",
                                marshu+"dime-coin-tail-thumb.jpg",
                                marshu+"quarter-coin-tail-thumb.jpg",
                                marshu+"half-dollar-coin-tail-thumb.jpg"]
                      }
        pass

    @command("^waddle$")
    def waddle(self, msg):
        dddcopypasta = u"\U0001F427 **King Dedede** \U0001F427 is definitely **top tier**. The king's got it all; disjoint \U00002694, power \U0001F4AA, recovery \U00002708, and damaging throw combos \U0001F4A5. He is the hardest character in the game to kill vertically \U0001F480, and with the safest and strongest ways to kill \U0001F480 being traditionally vertical, that's huge \U000026F0. His presence at the ledge is not to be ignored, as with clever Gordo setups, he can cover most if not all ledge options with a potentially deadly hitbox \U0001F480. He might be combo food \U0001F356, but he wants all that \U0001F4A2 rage \U0001F4A2 so he can kill with his safe and powerful back air \U0001F528 even earlier than usual. **An obvious member of \U0001F427 top tier\U0001F427.**"  # noqa E501
        kingistoptier = u"\U0001F427 **THE \U0001F427 KING \U0001F427 IS \U0001F427 TOP \U0001F427 TIER** \U0001F427"  # noqa E501
        self.say(msg.channel, "{}\n{}".format(dddcopypasta, kingistoptier))
        # self.say(msg.channel, "Waddle waddle, **motherfucker**")

    @command("^flip", access=-1)
    def flip(self, msg):
        coin = random.randint(0, 10)
        if (coin % 2 == 0):
            self.say(msg.channel, self.coins["heads"][int(coin/5)])
        else:
            tails = random.randint(0, 10)
            if (tails % 10 == 0):
                self.say(msg.channel, "https://puu.sh/rlzdJ/c9489a02b4.png")
            else:
                self.say(msg.channel, self.coins["tails"][int(coin/5)])
