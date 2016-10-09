"""
    Plugin Name : Nimious
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

"http://i.imgur.com/XpXoEDT.jpg"

from core.Plugin import Plugin
from core.Decorators import *
import logging

logger = logging.getLogger(__name__)


class Nimious(Plugin):
    def activate(self):
        pass

    @command("^[Ss]tryker *(?:when he)? *\"(.*)\"$", access=100)
    def strkyer(self, msg):
        self.say(msg.channel, "http://i.imgur.com/XpXoEDT.jpg")
        self.say(msg.channel, "^ Stryker when he {}".format(msg.arguments[0]))
