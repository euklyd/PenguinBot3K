"""
    Plugin Name : Macro
    Plugin Version : 0.1

    Description:
        Transforms text into text with a macro applied.

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

logger = logging.getLogger(__name__)

class Macro(Plugin):
    def activate(self):
        pass

    @command("^emojify ([\u263a-\U0001f645]) (.*)", access=-1)
    # @command(u"^emojify (.) (.*)*", access=-1)
    def emojify(self, msg):
        """`emojify <emoji> <sentence>`: replace all spaces in <sentence> with <emoji>"""
        logger.info(msg.arguments)
        emoji = msg.arguments[0]
        reply = msg.arguments[1].replace(' ', ' {} '.format(emoji))
        logger.info(reply)
        self.say(msg.channel, reply)
