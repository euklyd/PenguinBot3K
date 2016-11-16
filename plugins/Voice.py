"""
    Plugin Name : Voice
    Plugin Version : 0.1

    Description:
        Provides voice channel support, e.g., streaming music or some such.

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *

import discord

ACCESS = {
    'maestro': 200,
    'conductor': 500,
    'composer': 900
}


class Voice(Plugin):
    async def activate(self):
        # This shouldn't be needed; Linux should load the lib automatically.
        # discord.opus.load_opus(//some lib name)
        # discord.opus.load_opus("/Users/et/Documents/Code/virtualenv/py_standard/lib/python3.5/site-packages/discord/bin/libopus-0.x64.dll")
        self.voice = None
        self.player = None
        pass

    async def deactivate(self):
        if (self.voice is not None):
            self.voice.disconnect()

    @command("^joinvc <#([0-9]+)>", access=ACCESS['conductor'], name='joinvc',
             doc_brief=("`joinvc #<channel>`: Joins the voice channel "
             "`<channel>`."))
    async def joinvc(self, msg, arguments):
        # vc = await self.core.get_channel(arguments[0])
        vc = self.core.get_channel(arguments[0])
        try:
            if (self.voice is not None and self.voice.is_connected()):
                await self.core.move_to(vc)
            else:
                self.voice = await self.core.join_voice_channel(vc)
        except discord.InvalidArgument:
            await self.send_message(
                msg.channel,
                "**ERROR:** The channel you specified is not a voice channel."
            )

    @command("^tokusentai|TOKUSENTAI|\*\*TOKUSENTAI\*\*$",
             access=ACCESS['conductor'], name='joinvc',
             doc_brief=("`tokusentai`: Tokusentai\t*Tokusentai*\tTOKUSENTAI\t"
             "**TOKUSENTAI**"))
    async def tokusentai(self, msg, arguments):
        if (self.voice is None or self.voice.is_connected() is False):
            await self.send_message(
                msg.channel,
                "**ERROR:** I'm not connected to voice right now."
            )
            return
        tokusentai_src = "resources/music/05-sanjou-ginyu-tokusentai.mp3"
        self.player = self.voice.create_ffmpeg_player(tokusentai_src)
        self.player.start()
