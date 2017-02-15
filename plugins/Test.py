"""
    Plugin Name : Test
    Plugin Version : 0.0

    Description:
        Various testing things that shouldn't be actually used in practice.

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


class Test(Plugin):
    async def activate(self):
        pass

    async def deactivate(self):
        pass

    @command("^TEST$", name="test")
    async def test(self, msg, arguments):
        await self.send_message(msg.channel, "Testing: `ON`")

    # @filter("(?:^|[^\\])([Cc]+\W*[Uu]+\W*[Cc]+\W*[Kk]+)", name='cuckfilter',
    @filter("([Cc]+\W*[Uu]+\W*[Cc]+\W*[Kk]+)", name='cuckfilter',
            # server="190782508105728000")
            server="TEST")
    async def fuck_the_cuck(self, msg, arguments):
        content = msg.content.replace(arguments[0], "**{}**".format(arguments[0]))
        await self.send_message(
            msg.channel,
            "<@!{author}>\n"
            "> {content}\n\n"
            # "Did you mean 'Shezzy'?".format(
            "Did you mean <@!{shezzy}>?".format(
                author=msg.author.id, content=content,
                shezzy="208708372281819147")
        )
