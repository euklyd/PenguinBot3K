"""
    Plugin Name : Utility
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


class Utility(Plugin):
    def activate(self):
        pass

    @command("^waddle$")
    def waddle(self, msg):
        u"""`waddle`: Prints out the dankest of \U0001F427 Penguin \U0001F427 memes"""
        dddcopypasta = u"\U0001F427 **King Dedede** \U0001F427 is definitely **top tier**. The king's got it all; disjoint \U00002694, power \U0001F4AA, recovery \U00002708, and damaging throw combos \U0001F4A5. He is the hardest character in the game to kill vertically \U0001F480, and with the safest and strongest ways to kill \U0001F480 being traditionally vertical, that's huge \U000026F0. His presence at the ledge is not to be ignored, as with clever Gordo setups, he can cover most if not all ledge options with a potentially deadly hitbox \U0001F480. He might be combo food \U0001F356, but he wants all that \U0001F4A2 rage \U0001F4A2 so he can kill with his safe and powerful back air \U0001F528 even earlier than usual. **An obvious member of \U0001F427 top tier\U0001F427.**"  # noqa E501
        kingistoptier = u"\U0001F427 **THE \U0001F427 KING \U0001F427 IS \U0001F427 TOP \U0001F427 TIER** \U0001F427"  # noqa E501
        self.say(msg.channel, "{}\n{}".format(dddcopypasta, kingistoptier))

    @command("^pick-one (.*)", access=-1)
    def pick_one(self, msg):
        """`pick-one <list of items>`: Selects one item out of a list of space-separated items."""
        args = msg.arguments[0]
        items = args.split(' ')
        choice = random.choice(items)
        self.say(msg.channel, "<@!{}>, your selection is **{}**!".format(msg.sender, choice))
