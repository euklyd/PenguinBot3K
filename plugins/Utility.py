"""
    Plugin Name : Utility
    Plugin Version : 1.1

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

    @command("^pick-one (.*)", access=-1)
    def pick_one(self, msg):
        """`pick-one <list of items>`: Selects one item out of a list of space-separated items."""
        args = msg.arguments[0]
        items = args.split(' ')
        choice = random.choice(items)
        self.say(msg.channel, "<@!{}>, your selection is **{}**!".format(msg.sender, choice))


    @command("^repeat (.*)", access=900)
    def repeat(self, msg):
        self.say(msg.channel, msg.arguments[0])
        self.delete_message(msg)
