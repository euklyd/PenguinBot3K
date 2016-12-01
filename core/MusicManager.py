"""
    Class Name : MusicManager

    Description:
        Manages playing music and music queues and such.
        Controlled by plugins/Voice.py

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from abc import ABCMeta, abstractmethod

import asyncio
import discord
import logging
import mutagen
import os
import queue
import time


class Song(metaclass=ABCMeta):
    def __init__(self, title, requestor, channel):
        self.title = title
        self.requestor = requestor
        self.channel = channel
        self.logger = logging.getLogger("songs." + self.title)

    @abstractmethod
    def announcement(self):
        return

    @abstractmethod
    async def create_player(self, voice, after=None):
        return

# class YouTubeSong():
#     def __init__(self, yt_url, title, uploader, requestor, channel):
#         """
#             Arguments:
#                 yt_url (str):   URL of the YouTube video
#                 title (str):    Title of the video
#                 uploader (str): YouTube user who uploaded the video
#                 # duration (int): Duration of the video, in seconds
#                 requestor (discord.User):
#                                 User who requested this song
#                 channel (discord.Channel):
#                                 Channel in which this song was requested
#         """
#         self.url = yt_url
#         self.title = title
#         self.uploader = uploader
#         # self.duration = duration
#         self.requestor = requestor
#         self.channel = channel


class YouTubeSong(Song):
    def __init__(self, yt_url, title, uploader, requestor, channel):
        """
            Arguments:
                yt_url (str):   URL of the YouTube video
                title (str):    Title of the video
                uploader (str): YouTube user who uploaded the video
                # duration (int): Duration of the video, in seconds
                requestor (discord.User):
                                User who requested this song
                channel (discord.Channel):
                                Channel in which this song was requested
        """
        super().__init__(title, requestor, channel)
        self.url = yt_url
        # self.title = title
        self.uploader = uploader
        # self.duration = duration
        # self.requestor = requestor
        # self.channel = channel

    def announcement(self):
        announcement = ("**Now playing:** *{title}* [{{min}}:{{sec}}], "
                        "by {uploader}\n*Requested by {user}*").format(
            title=self.title,
            uploader=self.uploader,
            user=self.requestor.name
        )
        return announcement

    async def create_player(self, voice, after=None):
        self.logger.info("YouTubeSong: creating player")
        player = await voice.create_ytdl_player(self.url, after=after)
        return player


class MP3Song(Song):
    def __init__(self, name, requestor, channel):
        self.path = "resources/music/{}".format(name)
        metadata = mutagen.File(self.path)
        title = str(metadata['TIT2'])
        super().__init__(title, requestor, channel)
        self.name = name
        self.url = self.name
        # self.title = title
        # self.artist = artist
        # self.requestor = requestor
        # self.channel = channel
        # metadata = mutagen.File(self.path)
        # self.title = str(metadata['TIT2'])
        try:
            self.artist = str(metadata['TOPE'])
        except KeyError:
            self.artist = str(metadata['TCOM'])
        self.duration = metadata.info.length

    def announcement(self):
        announcement = ("**Now playing:** *{title}* [{{min}}:{{sec}}], "
                        "by {artist}\n*Requested by {user}*").format(
            title=self.title,
            artist=self.artist,
            user=self.requestor.name
        )
        return announcement

    async def create_player(self, voice, after=None):
        self.logger.info("MP3Song: creating player")
        player = await voice.create_ffmpeg_player(self.path, after=after)
        player.duration = self.duration
        return player


class PlaylistEntry():
    # def __init__(self, player, announcement, yt_song):
    #     self.player = player
    #     self.announcement = announcement
    #     self.yt_song = yt_song

    # def __init__(self, yt_song):
    #     self.player = None
    #     self.announcement = None
    #     self.yt_song = yt_song

    def __init__(self, song):
        self.player = None
        self.announcement = None
        self.song = song

    # async def load(self, voice, after=None):
    #     try:
    #         ## UPGRADE: Move this portion to yt_song.create_player() so that
    #         ##          it can also be used by other music types
    #         self.player = await voice.create_ytdl_player(
    #             self.yt_song.url, after=after
    #         )
    #     except:
    #         error_msg = "**ERROR:** Couldn't process request for {}".format(
    #             self.yt_song.title
    #         )
    #         return {'type': "error", 'response': error_msg}
    #     else:
    #         ## UPGRADE: Move this portion to yt_song.announcement() so that
    #         ##          it can also be used by other music types
    #         self.announcement = ("**Now playing:** *{title}* "
    #                              "[{min:0>2.0f}:{sec:0>2d}], by {uploader}\n"
    #                              "*Requested by {user}*").format(
    #             title=self.yt_song.title,
    #             min=self.player.duration / 60,
    #             sec=self.player.duration % 60,
    #             uploader=self.yt_song.uploader,
    #             user=self.yt_song.requestor.name
    #         )
    #         return {'type': "success", 'response': self.announcement}

    async def load(self, voice, after=None):
        # try:
        #     self.player = await self.song.create_player(voice, after=after)
        # except:
        #     error_msg = "**ERROR:** Couldn't process request for {}".format(
        #         self.song.title
        #     )
        #     return {'type': "error", 'response': error_msg}
        # else:
        #     self.announcement = song.announcement().format(
        #         min=self.player.duration / 60,
        #         sec=self.player.duration % 60,
        #     )
        #     return {'type': "success", 'response': self.announcement}
        self.player = await self.song.create_player(voice, after=after)
        self.announcement = self.song.announcement().format(
            min=self.player.duration / 60,
            sec=self.player.duration % 60,
        )
        return {'type': "success", 'response': self.announcement}


class MusicManager():
    def __init__(self, core):
        self.core = core
        self.logger = logging.getLogger("core.MusicManager")
        discord.opus.load_opus("/usr/lib/x86_64-linux-gnu/libopus.so.0")

        # self.voice = None
        # self.current_song = None
        # # self.player = None
        # # self.paused = False
        # self.playlist_queue = queue.Queue()
        # # self.yt_loop = asyncio.get_event_loop()
        #
        # self.reset = False
        # self.loop_closed = asyncio.Future()
        # self.play_next = asyncio.Event()
        #
        # self.core.loop.create_task(self.playlist_loop())

        self.start()

    # async def loop_player(self):
    #     while (true):
    #         await asyncio.sleep(1)
    #         if (self.paused is False and
    #                 self.player is not None and
    #                 self.player.is_playing() is False):
    #             await self.play_yt_song()

    def start(self):
        self.logger.info("Starting MusicManager")
        self.voice = None
        self.current_song = None
        self.playlist_queue = queue.Queue()
        self.reset = False
        self.loop_closed = asyncio.Future()
        self.play_next = asyncio.Event()
        self.core.loop.create_task(self.playlist_loop(future=self.loop_closed))

    async def close(self):
        self.logger.info("Closing MusicManager")
        if (self.voice is not None):
            await self.voice.disconnect()
        self.reset = True
        if (self.is_active()):
            await self.skip()
        await self.loop_closed
        self.logger.info("playlist_loop finished")

    def is_connected(self):
        if (self.voice is None or
                self.voice.is_connected() is False):
            return False
        else:
            return True

    def is_active(self):
        self.logger.debug(
            "is_active: self.is_connected: {}, self.current_song: {}".format(
                self.is_connected(), self.current_song)
        )
        if (self.is_connected() is False or self.current_song is None):
            return False
        else:
            return not self.current_song.player.is_done()

    def advance_queue(self):
        self.logger.info("advancing queue")
        self.core.loop.call_soon_threadsafe(self.play_next.set)

    async def playlist_loop(self, future):
        while (self.reset is False):
            # self.logger.info("playlist_loop looped")
            # if (self.reset):
            #     break
            # elif (self.is_connected() is False):
            if (self.is_connected() is False):
                self.logger.debug("playlist_loop: slept, not connected")
                await asyncio.sleep(1)
            elif (self.playlist_queue.empty()):
                self.logger.debug("playlist_loop: queue is empty, sleeping")
                await asyncio.sleep(1)
            else:
                self.logger.info("playlist_loop: playing next song")
                self.play_next.clear()
                self.logger.debug("getting next song")
                # self.current_song = await self.playlist_queue.get()
                self.current_song = self.playlist_queue.get()
                self.logger.debug("got next song")
                announcement = await self.current_song.load(
                    voice=self.voice, after=self.advance_queue
                )
                await self.core.send_message(
                    # self.current_song.yt_song.channel,
                    self.current_song.song.channel,
                    # self.current_song.announcement
                    announcement['response']
                )
                if (announcement['type'] == "error"):
                    pass
                else:
                    self.current_song.player.start()
                    await self.play_next.wait()
        future.set_result('closed')

    async def yt_add(self, yt_url, yt_embed, requestor, channel):
        song = YouTubeSong(
            yt_url=yt_url,
            title=yt_embed['title'],
            uploader=yt_embed['author']['name'],
            requestor=requestor,
            channel=channel,
        )
        self.logger.info("yt_add: Created song {}".format(yt_embed['title']))
        # try:
        #     player = await self.voice.create_ytdl_player(
        #         yt_url, after=self.advance_queue
        #     )
        # except:
        #     error_msg = "ERROR: Couldn't process request"
        #     return {'type': "error", 'response': error_msg}
        # else:
        #     announcement = ("**Now playing:** *{title}* "
        #                     "[{min:0>2.0f}:{sec:0>2d}], by {uploader}\n"
        #                     "*Requested by {user}*").format(
        #         title=song.title,
        #         min=player.duration / 60,
        #         sec=player.duration % 60,
        #         uploader=song.uploader,
        #         user=song.requestor.name
        #     )
        playlist_entry = PlaylistEntry(song)
        self.logger.info(
            "yt_add: Created playlist_entry {}".format(yt_embed['title'])
        )
        # self.playlist_queue.put(song)
        self.playlist_queue.put(playlist_entry)
        self.logger.info(
            "yt_add: Added playlist_entry {} to playlist_queue".format(
                yt_embed['title'])
        )
        response = ("Added *{title}*, by {uploader} to the playlist\n"
                    "*Requested by {user}*").format(
            title=song.title,
            uploader=song.uploader,
            user=song.requestor.name
        )
        return {'type': "success", 'response': response}

    async def mp3_add(self, name, requestor, channel):
        music_library = os.listdir("resources/music")
        if (name not in music_library):
            raise OSError("Song not found")
        song = MP3Song(name, requestor, channel)
        self.logger.info("mp3_add: Created song {}".format(song.title))
        playlist_entry = PlaylistEntry(song)
        self.logger.info(
            "mp3_add: Created playlist_entry {}".format(song.title)
        )
        self.playlist_queue.put(playlist_entry)
        self.logger.info(
            "mp3_add: Added playlist_entry {} to playlist_queue".format(
                song.title)
        )
        response = ("Added *{title}*, by {uploader} to the playlist\n"
                    "*Requested by {user}*").format(
            title=song.title,
            uploader=song.artist,
            user=song.requestor.name
        )
        return {'type': "success", 'response': response}

    # async def play_yt_song(self):
    #     if (self.playlist_queue.empty is False):
    #         yt_vid = self.playlist_queue.get()
    #         self.player = await self.voice.create_ytdl_player(
    #             yt_vid.url
    #         )
    #         announcement = ("**Now playing:** *{title}* "
    #                         "[{min:0>2.0f}:{sec:0>2d}] by {uploader}\n"
    #                         "*Requested by {user}*").format(
    #             title=yt_vid.title,
    #             min=self.player.duration / 60,
    #             sec=self.player.duration % 60,
    #             uploader=yt_vid.uploader,
    #             user=yt_vid.requestor
    #         )
    #         await self.core.send_message(yt_vid.channel, announcement)
    #         self.player.start()

    async def pause(self):
        if (self.is_connected() is False):
            return "**ERROR:** I'm not connected to voice right now."
        # elif (self.player.is_playing()):
        elif (self.is_active() is True):
            # self.paused = True
            # self.player.pause()
            self.current_song.player.pause()
            return None
        else:
            return "**ERROR:** I'm not even playing anything right now smh"

    async def resume(self):
        if (self.is_connected() is False):
            return "**ERROR:** I'm not connected to voice right now."
        elif (self.is_active() is False):
            # self.player.resume()
            self.current_song.player.resume()
            # self.paused = False
            return None

    async def skip(self):
        if (self.is_active()):
            self.logger.info("skipping song")
            self.current_song.player.stop()

    def list_library(self, album=""):
        library = os.listdir("resources/music/{}".format(album))
        self.logger.info(library)
        return library

    async def list_playlist(self):
        # playlist = list(self.playlist_queue.queue)
        # playlist.insert(0, self.current_song)
        return self.current_song, list(self.playlist_queue.queue)

    def get_current_url(self):
        # return self.current_song.yt_song.url
        return self.current_song.song.url

    async def join_voice_channel(self, channel):
        # if (self.voice is not None and self.voice.is_connected()):
        if (self.voice is not None):
            await self.voice.move_to(channel)
        else:
            self.voice = await self.core.join_voice_channel(channel)
