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

# module_trigger = "vc "


class Voice(Plugin):
    async def activate(self):
        # This shouldn't be needed; Linux should load the lib automatically.
        # discord.opus.load_opus("libopus-0.x64.dll")
        # discord.opus.load_opus("/usr/lib/x86_64-linux-gnu/libopus.so.0")
        # self.voice = None
        # self.player = None
        self.music_manager = self.core.music_manager

        # pass

    async def deactivate(self):
        self.music_manager.close()

    @command("^vc joinvc <#([0-9]+)>$", access=ACCESS['conductor'], name='joinvc',
             doc_brief=("`vc joinvc #<channel>`: Joins the voice channel "
             "`<channel>`."))
    async def joinvc(self, msg, arguments):
        # vc = await self.core.get_channel(arguments[0])
        vc = self.core.get_channel(arguments[0])
        try:
            # if (self.voice is not None and self.voice.is_connected()):
            #     await self.voice.move_to(vc)
            # else:
            #     self.voice = await self.core.join_voice_channel(vc)
            await self.music_manager.join_voice_channel(vc)
        except discord.InvalidArgument:
            await self.send_message(
                msg.channel,
                "**ERROR:** The channel you specified is not a voice channel."
            )

    # @command("^vc tokusentai|TOKUSENTAI|\*\*TOKUSENTAI\*\*$",
    #          access=ACCESS['maestro'], name='tokusentai',
    #          doc_brief=("`vc tokusentai`: Tokusentai\t*Tokusentai*\t"
    #          "TOKUSENTAI\t**TOKUSENTAI**"))
    # async def tokusentai(self, msg, arguments):
    #     if (self.voice is None or self.voice.is_connected() is False):
    #         await self.send_message(
    #             msg.channel,
    #             "**ERROR:** I'm not connected to voice right now."
    #         )
    #         return
    #     if (self.player is not None and self.player.is_playing()):
    #         self.player.stop()
    #     tokusentai_src = "resources/music/05-sanjou-ginyu-tokusentai.mp3"
    #     self.player = self.voice.create_ffmpeg_player(tokusentai_src)
    #     self.player.start()

    # @command("^vc yt play (https?:\/\/www\.youtube\.com\/watch\?v=.*)$",
    #          access=ACCESS['maestro'], name='yt play',
    #          doc_brief="`vc yt play <youtube_url>`: Plays the audio from a "
    #          "YouTube video specified by `<youtube_url>`.")
    # async def yt_play(self, msg, arguments):
    #     if (self.voice is None or self.voice.is_connected() is False):
    #         await self.send_message(
    #             msg.channel,
    #             "**ERROR:** I'm not connected to voice right now."
    #         )
    #         return
    #     if (self.player is not None and self.player.is_playing()):
    #         self.player.stop()
    #     self.player = await self.voice.create_ytdl_player(arguments[0])
    #     await self.delete_message(msg)
    #     self.player.start()
    #     reply = ("**Now playing:** *{title}* [{min:0>2.0f}:{sec:0>2d}] by {uploader}\n"
    #              "*Requested by {user}*").format(
    #         title=msg.embeds[0]['title'],
    #         min=self.player.duration / 60,
    #         sec=self.player.duration % 60,
    #         uploader=msg.embeds[0]['author']['name'],
    #         user=msg.author.name
    #     )
    #     await self.send_message(msg.channel, reply)

    @command("^vc yt queue (https?:\/\/www\.youtube\.com\/watch\?v=.*)$",
             access=-1, name='yt queue',
             doc_brief="`vc yt queue <youtube_url>`: Queues the audio from a "
             "YouTube video specified by `<youtube_url>`.")
    async def yt_queue(self, msg, arguments):
        try:
            response = await self.music_manager.yt_add(
                arguments[0], msg.embeds[0], msg.author, msg.channel
            )
            await self.send_message(msg.channel, response['response'])
        except IndexError:
            await self.send_message(
                msg.channel,
                ("**ERROR:** Error in parsing the video embed; please try again\n"
                 "Request: `{}`").format(msg.content)
            )
        await self.delete_message(msg)

    @command("^vc pause$", access=ACCESS['maestro'], name='pause',
             doc_brief="`vc pause`: Pause the music.")
    async def pause(self, msg, arguments):
        # if (self.voice is None or self.voice.is_connected() is False):
        #     await self.send_message(
        #         msg.channel,
        #         "**ERROR:** I'm not connected to voice right now."
        #     )
        # elif (self.player.is_playing()):
        #     self.player.pause()
        # else:
        #     await self.send_message(
        #         msg.channel,
        #         "**ERROR:** I'm not even playing anything right now smh"
        #     )
        error = await self.music_manager.pause()
        if (error is not None):
            await self.send_message(msg.channel, error)

    @command("^vc resume$", access=ACCESS['maestro'], name='resume',
             doc_brief="`vc resume`: Resume the music.")
    async def resume(self, msg, arguments):
        # if (self.voice is None or self.voice.is_connected() is False):
        #     await self.send_message(
        #         msg.channel,
        #         "**ERROR:** I'm not connected to voice right now."
        #     )
        # else:
        #     self.player.resume()
        error = await self.music_manager.resume()
        if (error is not None):
            await self.send_message(msg.channel, error)

    @command("^vc skip$", access=ACCESS['maestro'], name='skip',
             doc_brief="`vc skip`: Move to next song in the playlist.")
    async def skip(self, msg, arguments):
        await self.music_manager.skip()

    @command("^vc playlist$", access=-1, name='playlist',
             doc_brief="`vc playlist`: Show current playlist.")
    async def show_playlist(self, msg, arguments):
        current_song, playlist = await self.music_manager.list_playlist()
        reply = "**Current YouTube Playlist:**\n"
        reply += ("🔊 ** -*{song}***, by {uploader} "
                  "(requested by {requestor})\n").format(
            song=current_song.yt_song.title,
            uploader=current_song.yt_song.uploader,
            requestor=current_song.yt_song.requestor
        )
        for song in playlist:
            reply += ("** -*{song}***, by {uploader} "
                      "(requested by {requestor})\n").format(
                song=song.yt_song.title,
                uploader=song.yt_song.uploader,
                requestor=song.yt_song.requestor
            )
        await self.send_message(msg.channel, reply)

    @command("^vc url$", access=-1, name='show url',
             doc_brief="`vc url`: Shows the URL of the current song.")
    async def show_url(self, msg, arguments):
        url = self.music_manager.get_current_url
        self.send_message(msg.channel, "Current URL: {}".format(url))

    @command("^vc reset$", access=ACCESS['composer'], name='reset',
             doc_brief="`vc reset`: Resets the entire music module.")
    async def reset(self, msg, arguments):
        self.send_message(
            msg.channel, "Attempting to restart {}".format(self.__name__)
        )
        await self.music_manager.close()
        self.music_manager.start()
