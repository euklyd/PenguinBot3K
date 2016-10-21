"""
    Plugin Name : Macro
    Plugin Version : 1.0

    Description:
        Transforms text into text with a macro applied.

    Contributors:
        - Euklyd / Popguin

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
    @command("^emojify ([\u2600-\u26FF\u2700-\u27BF\U0001F1E6-\U0001F1FF\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF]|(?:<:[A-Za-z0-9_]*:\d*>)) (.*)", access=-1)
    def emojify(self, msg):
        """`emojify <emoji> <sentence>`: replace all spaces in `<sentence>` with `<emoji>`"""
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

    @command("^emojify-full \"(.*|(?:<:.*:\d*>))\" (.*)", access=-1)
    def emojify_full(self, msg):
        logger.info(msg.arguments)
        emoji = msg.arguments[0]
        reply = msg.arguments[1].replace(' ', ' {} '.format(emoji))
        reply = "<@!{}>: {}".format(msg.sender, reply)
        logger.info(reply)
        self.say(msg.channel, reply)
        self.delete_message(msg)

    @command("^waddle$", access=100)
    def waddle(self, msg):
        u"""`waddle`: Prints out the dankest of \U0001F427 Penguin \U0001F427 memes"""
        dddcopypasta = u"\U0001F427 **King Dedede** \U0001F427 is definitely **top tier**. The king's got it all; disjoint \U00002694, power \U0001F4AA, recovery \U00002708, and damaging throw combos \U0001F4A5. He is the hardest character in the game to kill vertically \U0001F480, and with the safest and strongest ways to kill \U0001F480 being traditionally vertical, that's huge \U000026F0. His presence at the ledge is not to be ignored, as with clever Gordo setups, he can cover most if not all ledge options with a potentially deadly hitbox \U0001F480. He might be combo food \U0001F356, but he wants all that \U0001F4A2 rage \U0001F4A2 so he can kill with his safe and powerful back air \U0001F528 even earlier than usual. **An obvious member of \U0001F427 top tier\U0001F427.**"  # noqa E501
        kingistoptier = u"\U0001F427 **THE \U0001F427 KING \U0001F427 IS \U0001F427 TOP \U0001F427 TIER** \U0001F427"  # noqa E501
        self.say(msg.channel, "{}\n{}".format(dddcopypasta, kingistoptier))
