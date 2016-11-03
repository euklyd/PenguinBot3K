"""
    Plugin Name : Macro
    Plugin Version : 2.0

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
    async def activate(self):
        pass

    # @command("^emojify ([\u263a-\U0001f645]|(?:<:.*:\d*>)) (.*)", access=-1)
    @command("^emojify ([\u2600-\u26FF\u2700-\u27BF\U0001F1E6-\U0001F1FF\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF]|(?:<:[A-Za-z0-9_]*:\d*>)) (.*)", access=-1)
    async def emojify(self, msg, arguments):
        """`emojify <emoji> <sentence>`: replace all spaces in `<sentence>` with `<emoji>`"""
        """
        0x1F600...0x1F64F, // Emoticons
        0x1F300...0x1F5FF, // Misc Symbols and Pictographs
        0x1F680...0x1F6FF, // Transport and Map
        0x2600...0x26FF,   // Misc symbols
        0x2700...0x27BF,   // Dingbats
        0xFE00...0xFE0F    // Variation Selectors
        """
        self.logger.debug(arguments)
        emoji = arguments[0]
        reply = arguments[1].replace(' ', ' {} '.format(emoji))
        reply = "<@!{}>: {}".format(msg.author.id, reply)
        self.logger.info(reply)
        await self.send_message(msg.channel, reply)
        await self.delete_message(msg)

    @command("^emojify -f \"(.*|(?:<:.*:\d*>)*)\" (.*)", access=-1)
    async def emojify_full(self, msg, arguments):
        self.logger.debug(arguments)
        emoji = arguments[0]
        reply = arguments[1].replace(' ', ' {} '.format(emoji))
        reply = "<@!{}>: {}".format(msg.author.id, reply)
        self.logger.info(reply)
        await self.send_message(msg.channel, reply)
        await self.delete_message(msg)

    @command("^emojify -w \"(.*|(?:<:.*:\d*>))\" (.*)", access=50)
    async def emojify_whisper(self, msg, arguments):
        """`emojify -w "<emoji>" <sentence>`: as standard `emojify -f`, but sends output to the user in a DM."""
        self.logger.debug(arguments)
        emoji = arguments[0]
        reply = arguments[1].replace(' ', ' {} '.format(emoji))
        reply = "<@!{}>: {}".format(msg.author.id, reply)
        self.logger.info(reply)
        await self.send_whisper(msg.author, reply)
        await self.delete_message(msg)

    @command("^waddle$", access=100)
    async def waddle(self, msg, arguments):
        u"""`waddle`: Prints out the dankest of \U0001F427 Penguin \U0001F427 memes"""
        dddcopypasta = u"\U0001F427 **King Dedede** \U0001F427 is definitely **top tier**. The king's got it all; disjoint \U00002694, power \U0001F4AA, recovery \U00002708, and damaging throw combos \U0001F4A5. He is the hardest character in the game to kill vertically \U0001F480, and with the safest and strongest ways to kill \U0001F480 being traditionally vertical, that's huge \U000026F0. His presence at the ledge is not to be ignored, as with clever Gordo setups, he can cover most if not all ledge options with a potentially deadly hitbox \U0001F480. He might be combo food \U0001F356, but he wants all that \U0001F4A2 rage \U0001F4A2 so he can kill with his safe and powerful back air \U0001F528 even earlier than usual. **An obvious member of \U0001F427 top tier\U0001F427.**"  # noqa E501
        kingistoptier = u"\U0001F427 **THE \U0001F427 KING \U0001F427 IS \U0001F427 TOP \U0001F427 TIER** \U0001F427"  # noqa E501
        await self.send_message(msg.channel, "{}\n{}".format(dddcopypasta, kingistoptier))

    @command("^plumber$", access=100)
    async def plumber(self, msg, arguments):
        u"""`plumber`: Prints out the dankest of 🚽 Plumber 🚽 memes"""
        mariocopypasta = u"<:mario:234535787117543425> Mario <:mario:234535787117543425> is definitely **not top tier**. The plumber's got nothing; no range ✖  , no power 😩  , mediocre recovery 😐  , and bad matchups <:sunglasses_mewtwo:230828762453770240> ☁ He isn't very fast 🐢 , and he doesn't have any strong kill set ups like other top tiers 🍌 ⬇ 👏 ⬆ ✊ The only reason Ally and ANTi were able to win supermajors with him 🏆 is because of **pure skill** , and we will be blessed 🙏  if we ever see two top players carry an upper mid-tier so far again. Obviously **not** a member of the <:mario:234535787117543425> top tier <:mario:234535787117543425>"
        await self.send_message(msg.channel, mariocopypasta)
