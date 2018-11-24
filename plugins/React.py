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
import json
import logging
import random
import re

path = "resources/filter/{}"

with open(path.format('reactservers.json')) as rsfile:
    reactservers = json.load(rsfile)


class React(Plugin):
    async def activate(self):
        pass

    @filter("^what$", name='what', server=reactservers)
    async def what(self, msg, arguments):
        lemonbot = self.core.emoji.any_emoji(['lemonbot', 'lemon_bot'])
        await self.add_reaction(msg, lemonbot)
        if (random.randint(0, 17) == 0):
            await self.add_reaction(msg, self.core.emoji.any_emoji(['refabot']))

    @filter("pregam(e|ing)", name='pregaming', server=[
            '328399532368855041', '436953982322081803', '258160125016014848',
            '474037724551315456', '459150872371265538', '363831487382028308'],
            flags=re.IGNORECASE)
    async def pregaming(self, msg, arguments):
        pregaming = self.core.emoji.any_emoji(['pregaming'])
        await self.add_reaction(msg, pregaming)

    @filter("^<:expand:[0-9]{16,20}>$", name='expand dong',
            server="190782508105728000")
    async def expand_dong(self, msg, arguments):
        expand = self.core.emoji.any_emoji(['expand'])
        dong = self.core.emoji.any_emoji(['dong'])
        await self.add_reaction(msg, expand)
        await self.add_reaction(msg, dong)

    @filter("^<:(?:fe1_)?([Cc]ain|[Aa]bel):[0-9]{16,20}>$", name='christmas cavaliers',
            server=reactservers)
    async def fe1_cavs(self, msg, arguments):
        if (arguments[0].lower() == 'cain'):
            cav = self.core.emoji.any_emoji(['fe1_abel', 'abel'])
        else:
            cav = self.core.emoji.any_emoji(['fe1_cain', 'cain'])
        await self.add_reaction(msg, cav)

    @filter("^<:.*(sonic|sanic).*:[0-9]{16,20}>$", name='sanic 3 & nipples',
            server='190782508105728000')
    async def sanic3(self, msg, arguments):
        nipples = self.core.emoji.any_emoji([
            'nipples_the_enchilada', 'nipples'
        ])
        await self.add_reaction(msg, nipples)

    @filter("^.*$", name='catface', server=['320996033268154378', '469635806852808704'])
    async def catface(self, msg, arguments):
        if (msg.channel.id in ['332721908019625989', '469720604191227905'] and
                msg.content != ":3"):
            await self.delete_message(msg)
            tsktsk = await self.send_message(
                msg.channel,
                '*We have rules here, heretic :3*'
            )
            await asyncio.sleep(5)
            await self.delete_message(tsktsk)

    @filter("^<:(?:harold|GLORY_TO_THRACIA):[0-9]{16,20}>$", name='in america',
            server='190782508105728000')
    async def in_america(self, msg, arguments):
        if (random.randint(0, 17) == 0):
            await self.add_reaction(msg, '🇨🇦')
        else:
            await self.add_reaction(msg, '🇺🇸')

    @filter("^<:YEAH_WEED:[0-9]{16,20}>$", name='YEAH_CANADA',
            server='190782508105728000')
    async def yeah_canada(self, msg, arguments):
        if (random.randint(0, 17) == 0):
            await self.add_reaction(msg, '🇨🇦')
        else:
            await self.add_reaction(msg, '🇺🇸')
