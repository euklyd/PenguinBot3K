"""
    Plugin Name : React
    Plugin Version : 0.1

    Description:
        Applies reactions to messages that match a filter

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *

import asyncio
import discord
import logging


class React(Plugin):
    async def activate(self):
        pass

    @filter("^what$", name='what', server="190782508105728000")
    async def what(self, msg, arguments):
        # lemonbot = self.core.emoji.emoji_str(["lemonbot", "lemon_bot"])
        # if (lemonbot[0] == '`'):
        #     self.logger.warning("no such emoji: {}".format(lemonbot))
        # else:
            # await self.add_reaction(msg, lemonbot)
        lemonbot = self.core.emoji.emoji(msg.server, ["lemonbot", "lemon_bot"])
        await self.add_reaction(msg, lemonbot)

    @filter("^<:expand:[0-9]{16,20}>$", name='expand dong',
            server="190782508105728000")
    async def expand_dong(self, msg, arguments):
        expand = self.core.emoji.emoji(msg.server, ["expand"])
        dong = self.core.emoji.emoji(msg.server, ["dong"])
        await self.add_reaction(msg, expand)
        await self.add_reaction(msg, dong)
