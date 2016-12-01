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

import asyncio
import discord
import re

ACCESS = {
    'user':      100,
    'maestro':   200,
    'conductor': 500,
    'composer':  900
}

# module_trigger = "vc "


class Voice(Plugin):
    async def activate(self):
        # This shouldn't be needed; Linux should load the lib automatically.
        # discord.opus.load_opus("libopus-0.x64.dll")
        # discord.opus.load_opus("/usr/lib/x86_64-linux-gnu/libopus.so.0")
        # self.voice = None
        # self.player = None
        await self.core.wait_until_login()
        self.music_manager = self.core.music_manager

        # pass

    async def deactivate(self):
        await self.music_manager.close()

    @command("^vc joinvc <#([0-9]+)>$", access=ACCESS['conductor'],
             name='joinvc', doc_brief=("`vc joinvc #<channel>`: "
             "Joins the voice channel `<channel>`."))
    async def joinvc(self, msg, arguments):
        vc = self.core.get_channel(arguments[0])
        try:
            await self.music_manager.join_voice_channel(vc)
            await self.send_message(
                msg.channel, "Joined voice channel <#{}>".format(arguments[0])
            )
        except discord.InvalidArgument:
            await self.send_message(
                msg.channel,
                "**ERROR:** The channel you specified is not a voice channel."
            )

    @command("^vc library$", access=-1, name='library',
             doc_brief="`vc library`: List all songs stored in "
             "the local library (in a private message).")
    async def list_library(self, msg, arguments):
        songs = self.music_manager.list_library().sort()
        reply = "**Music Library:**\n"
        for song in songs:
            reply += "- {}\n".format(song)
        await self.send_message(msg.author, reply)

    @command("^vc queue (.*)$", access=-1, name='local queue',
             doc_brief="`vc queue <song_name>`: Queue the audio from "
             "a local file named `<song_name>` (if it exists).")
    async def local_queue(self, msg, arguments):
        song_name = arguments[0]
        try:
            response = await self.music_manager.mp3_add(
                song_name, msg.author, msg.channel
            )
        except OSError:
            response = ("Song not found; use `vc library` to see"
                        "available selections.")
        await self.send_message(msg.channel, response)
        await asyncio.sleep(1)
        await self.delete_message(msg)

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

    @command("^vc yt queue (https?:\/\/www\.youtube\.com\/watch\?v=.*)$",
             access=-1, name='yt queue',
             doc_brief="`vc yt queue <youtube_url>`: Queue the audio from "
             "a YouTube video specified by `<youtube_url>`.")
    async def yt_queue(self, msg, arguments):
        error_msg = None
        try:
            await asyncio.sleep(0.5)
            response = await self.music_manager.yt_add(
                arguments[0], msg.embeds[0], msg.author, msg.channel
            )
            await self.send_message(msg.channel, response['response'])
        except IndexError:
            error_msg = await self.send_message(
                msg.channel,
                ("**ERROR:** Error in parsing the video embed; "
                 "please try again\n"
                 "Request: `{}`").format(msg.content)
            )
        await asyncio.sleep(1)
        await self.delete_message(msg)
        if (error_msg is not None):
            self.logger.info(
                "Error message w/ ID {} in response to Message ID {} "
                "to be deleted in 30 seconds.".format(error_msg.id, msg.id)
            )
            ## Why doesn't this work???
            await asyncio.sleep(30)
            await self.delete_message(error_msg)
            self.logger.info(
                "Error message w/ ID {} deleted.".format(error_msg.id)
            )

    @command("^vc yt bulk queue (.*)$", access=ACCESS['user'],
             name='yt bulk queue',
             doc_brief="`vc yt bulk queue <youtube_url1> <youtube_url2> ...`: "
             "Queue the audio from multiple YouTube videos.")
    async def yt_bulk_queue(self, msg, arguments):
        urls = arguments[0].split(' ')
        valid = []
        yt_pattern = "https?:\/\/(?:www\.youtube\.com\/watch\?v=|youtu.be\/)[0-9A-Za-z_\-]{11}"
        yt_regex = re.compile(yt_pattern)
        for url in urls:
            m = yt_regex.match(url)
            if (m is not None):
                valid.append(url)
        if (len(valid) != len(msg.embeds)):
            self.send_message(
                msg.channel,
                "something went wrong with parsing the embeds"
            )
        else:
            for i in range(0, len(valid)):
                await asyncio.sleep(1)
                try:
                    response = await self.music_manager.yt_add(
                        valid[i], msg.embeds[i], msg.author, msg.channel
                    )
                    await self.send_message(msg.channel, response['response'])
                except IndexError:
                    await self.send_message(
                        msg.channel,
                        ("**ERROR:** Error in parsing the video embed; "
                         "please try again\n"
                         "Request: `{}`").format(msg.content)
                    )
                    self.logger.info("Embed: {}".format(msg.embeds[i]))
                    self.logger.info("URL:   {}".format(valid[i]))
        await self.delete_message(msg)

    @command("^vc pause$", access=ACCESS['maestro'], name='pause',
             doc_brief="`vc pause`: Pause the music.")
    async def pause(self, msg, arguments):
        error = await self.music_manager.pause()
        if (error is not None):
            await self.send_message(msg.channel, error)

    @command("^vc resume$", access=ACCESS['maestro'], name='resume',
             doc_brief="`vc resume`: Resume the music.")
    async def resume(self, msg, arguments):
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
        if (current_song is not None):
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
                # if (len(reply) > 1500):
                #     await self.send_message(msg.channel, reply)
                #     reply = ""
        else:
            reply += "Playlist is empty!"
        if (len(reply) > 2000):
            reply = "**Next Ten Songs in YouTube Playlist:**\n"
            if (current_song is not None):
                reply += ("🔊 ** -*{song}***, by {uploader} "
                          "(requested by {requestor})\n").format(
                    song=current_song.yt_song.title,
                    uploader=current_song.yt_song.uploader,
                    requestor=current_song.yt_song.requestor
                )
            for i in range(0, 10):
                try:
                    line = ("** -*{song}***, by {uploader} "
                            "(requested by {requestor})\n").format(
                        song=playlist[i].yt_song.title,
                        uploader=playlist[i].yt_song.uploader,
                        requestor=playlist[i].yt_song.requestor
                    )
                    if (len(reply) + len(line) > 1950):
                        break
                    else:
                        reply += line
                except IndexError:
                    break
            reply += "...followed by others."
        # if (reply != ""):
        #     await self.send_message(msg.channel, reply)
        await self.send_message(msg.channel, reply)

    @command("^vc url$", access=-1, name='show url',
             doc_brief="`vc url`: Shows the URL of the current song.")
    async def show_url(self, msg, arguments):
        url = self.music_manager.get_current_url()
        await self.send_message(msg.channel, "Current URL: {}".format(url))

    @command("^vc reset$", access=ACCESS['composer'], name='reset',
             doc_brief="`vc reset`: Resets the entire music module.")
    async def reset(self, msg, arguments):
        await self.send_message(
            msg.channel,
            "Attempting to restart {}".format(
                type(self.music_manager).__name__)
        )
        await self.music_manager.close()
        await self.send_message(
            msg.channel,
            "Successfully closed {}".format(
                type(self.music_manager).__name__)
        )
        self.music_manager.start()
        await self.send_message(
            msg.channel,
            "Successfully restarted {}".format(
                type(self.music_manager).__name__)
        )
