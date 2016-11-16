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
        # discord.opus.load_opus("libopus-0.x64.dll")
        discord.opus.load_opus("/usr/lib/x86_64-linux-gnu/libopus.so.0")
        self.voice = None
        self.player = None
        pass

    async def deactivate(self):
        if (self.voice is not None):
            self.voice.disconnect()

    @command("^vc joinvc <#([0-9]+)>", access=ACCESS['conductor'], name='joinvc',
             doc_brief=("`vc joinvc #<channel>`: Joins the voice channel "
             "`<channel>`."))
    async def joinvc(self, msg, arguments):
        # vc = await self.core.get_channel(arguments[0])
        vc = self.core.get_channel(arguments[0])
        try:
            if (self.voice is not None and self.voice.is_connected()):
                await self.voice.move_to(vc)
            else:
                self.voice = await self.core.join_voice_channel(vc)
        except discord.InvalidArgument:
            await self.send_message(
                msg.channel,
                "**ERROR:** The channel you specified is not a voice channel."
            )

    @command("^vc tokusentai|TOKUSENTAI|\*\*TOKUSENTAI\*\*$",
             access=ACCESS['maestro'], name='tokusentai',
             doc_brief=("`vc tokusentai`: Tokusentai\t*Tokusentai*\t"
             "TOKUSENTAI\t**TOKUSENTAI**"))
    async def tokusentai(self, msg, arguments):
        if (self.voice is None or self.voice.is_connected() is False):
            await self.send_message(
                msg.channel,
                "**ERROR:** I'm not connected to voice right now."
            )
            return
        if (self.player is not None and self.player.is_playing()):
            self.player.stop()
        tokusentai_src = "resources/music/05-sanjou-ginyu-tokusentai.mp3"
        self.player = self.voice.create_ffmpeg_player(tokusentai_src)
        self.player.start()

    @command("^vc yt play (https:\/\/www\.youtube\.com\/watch\?v=.*)$",
             access=ACCESS['maestro'], name='yt play',
             doc_brief="`vc yt play <youtube_url>`: Plays the audio from a "
             "YouTube vido specified by `<youtube_url>`.")
    async def yt_play(self, msg, arguments):
        if (self.voice is None or self.voice.is_connected() is False):
            await self.send_message(
                msg.channel,
                "**ERROR:** I'm not connected to voice right now."
            )
            return
        if (self.player is not None and self.player.is_playing()):
            self.player.stop()
        self.player = self.voice.create_ytdl_player(arguments[0])
        self.player.start()

    @command("^vc pause$", access=ACCESS['maestro'], name='pause',
             doc_brief="`vc pause`: Pause the music.")
    async def pause(self, msg, arguments):
        if (self.voice is None or self.voice.is_connected() is False):
            await self.send_message(
                msg.channel,
                "**ERROR:** I'm not connected to voice right now."
            )
        elif (self.player.is_playing()):
            self.player.pause()
        else:
            await self.send_message(
                msg.channel,
                "**ERROR:** I'm not even playing anything right now smh"
            )

    @command("^vc resume$", access=ACCESS['maestro'], name='resume',
             doc_brief="`vc resume`: Resume the music.")
    async def resume(self, msg, arguments):
        if (self.voice is None or self.voice.is_connected() is False):
            await self.send_message(
                msg.channel,
                "**ERROR:** I'm not connected to voice right now."
            )
        else:
            self.player.resume()
