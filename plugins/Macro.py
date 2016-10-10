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

    # @command("^emojify ([\u263a-\U0001f645]|(?:<:.*:\d*>)) (.*)", access=-1)
    @command("^emojify ([\u2600-\u26FF\u2700-\u27BF\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF]|(?:<:.*:\d*>)) (.*)", access=-1)
    def emojify(self, msg):
        """`emojify <emoji> <sentence>`: replace all spaces in <sentence> with <emoji>"""
        """
        0x1F600...0x1F64F, // Emoticons
        0x1F300...0x1F5FF, // Misc Symbols and Pictographs
        0x1F680...0x1F6FF, // Transport and Map
        0x2600...0x26FF,   // Misc symbols
        0x2700...0x27BF,   // Dingbats
        0xFE00...0xFE0F    // Variation Selectors
        """
        logger.info(msg.arguments)
        emoji = msg.arguments[0]
        reply = msg.arguments[1].replace(' ', ' {} '.format(emoji))
        reply = "<@!{}>: {}".format(msg.sender, reply)
        logger.info(reply)
        self.say(msg.channel, reply)
        self.delete_message(msg)

    @command("^emojify-full \"(.|(?:<:.*:\d*>))\" (.*)", access=-1)
    def emojify_full(self, msg):
        logger.info(msg.arguments)
        emoji = msg.arguments[0]
        reply = msg.arguments[1].replace(' ', ' {} '.format(emoji))
        reply = "<@!{}>: {}".format(msg.sender, reply)
        logger.info(reply)
        self.say(msg.channel, reply)
        self.delete_message(msg)
