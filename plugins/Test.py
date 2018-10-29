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
import random
import string

from datetime import datetime


class Test(Plugin):
    async def activate(self):
        pass

    async def deactivate(self):
        pass

    @command("^TEST$", name="test")
    async def test(self, msg, arguments):
        await self.send_message(msg.channel, "Testing: `ON`")

    @command("^emtest (\d+) (\d+) (\d+)$", name="test")
    async def em_test(self, msg, arguments):
        desc_len  = int(arguments[0])
        n_fields  = int(arguments[1])
        field_len = int(arguments[2])

        desc = ''.join(random.choices(string.ascii_uppercase + string.digits, k=desc_len))
        em = discord.Embed(
            title='here u go iris',
            color=msg.author.color,
            description=desc,
            timestamp=datetime.now()
        )
        for i in range(0, n_fields):
            em.add_field(name='field {}'.format(i), value=''.join(random.choices(string.ascii_uppercase + string.digits, k=field_len)))
        await self.send_message(msg.channel, embed=em)

    @command("^spam <#(\d+)> `(.*)` every (\d+ (?:sec|min)) for (\d+ (?:min|hours?))",
             access=1000, name='spam')
    async def spam(self, msg, arguments):
        text = arguments[1]
        period = 60
        duration = 3600
        if ("min" in arguments[2]):
            period = int(arguments[2].split(' ')[0]) * 60
        else:
            period = int(arguments[2].split(' ')[0])
        if ("min" in arguments[3]):
            duration = int(arguments[3].split(' ')[0]) * 60
        else:
            duration = int(arguments[3].split(' ')[0]) * 60 * 60
        repetitions = duration/period
        while repetitions > 0:
            repetitions -= 1
            await self.send_message(msg.channel_mentions[0], text)
            await asyncio.sleep(period)
        await self.send_message(msg.channel_mentions[0], text)
        await self.send_message(msg.channel_mentions[0], f"Done spamming `{text}`.")

    # @command("^test playlist embed$", name="test playlist embed")
    # async def playlist_embed(self, msg, arguments):
    #     now_playing = ("Darius Gaiden (Arcade) - 01 - VISIONNERZ Arrange Version", "CaptainGordonVGM", "(Nightmarre#5295)")
    #     playlist = [
    #         ("Darius Gaiden - VISIONNERZ Music", "Video Game Music", "Nightmarre#5295"),
    #         ("Brigandine Legend of Forsena OST ► Carleon Map BGM", "AGC Adam Stephensons", "Nightmarre#5295"),
    #         ("Brigandine- Carleon Attack", "Paul John Sumaya", "Nightmarre#5295"),
    #         ("Final Fantasy VII - Main Theme [HQ]", "Cloud183", "Nightmarre#5295"),
    #         ("Paper Mario - Bowser, King of the Koopas (In-Game Ver.)", "Usagi-Chan", "Jedisupersonic#2765"),
    #         ("[HQ] Ys VI Napishtim Opening", "Galaga Forever", "Jedisupersonic#2765"),
    #         ("Dynasty Tactics 2 Soundtrack - Sun Ce's Theme", "squallimdying", "Jedisupersonic#2765"),
    #         ("Axelay (SNES) - Colony", "AccelJoe", "Nightmarre#5295"),
    #         ("Ogre Battle - Accretion Disk", "spokompton1983", "Jedisupersonic#2765"),
    #     ]
    #
    #     user = msg.server.get_member(self.core.user.id)
    #     em = discord.Embed(color=user.color)
    #     em.add_field(name=now_playing[0], value="{} (requested by {})".format(now_playing[1], now_playing[2]), inline=True)
    #     # em.add_field(name="Uploader/Artist", value=now_playing[1], inline=True)
    #     # em.add_field(name="Requestor", value=now_playing[2], inline=True)
    #     for song in playlist:
    #         # em.add_field(name=song[0], value=song[1], inline=False)
    #         # em.add_field(name="Uploader/Artist", value=song[1], inline=True)
    #         # em.add_field(name="Requestor", value=song[2], inline=True)
    #         em.add_field(name=song[0], value="{} (requested by {})".format(song[1], song[2]), inline=False)
    #     await self.send_message(msg.channel, embed=em)
    #
    # @command("^access testing$", name="access testing", access=500)
    # async def access_testing(self, msg, arguments):
    #     await self.send_message(msg.channel, "You have permission for this!")
