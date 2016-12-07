"""
    Class Name : MusicManager
    Class Version: 2.0

    Description:
        Manages playing music and music queues and such.
        Controlled by plugins/Voice.py

        Local music should be stored in `resources/music/`,
        preferably grouped by album, e.g.,
            `resources/music/Kilroy\ Was\ Here/Mr.\ Roboto.mp3`

        The MusicManager module is tested to work with the
        following music filetypes:
            - MP3
        may possibly work with:
            - AIFF
            - True Audio
        and can be extended to work with others (using the Mutagen
        library). One could also dumb it down and not bother with
        metadata, but that shouldn't be necessary for most
        applications. Besides, it's much prettier this way! =)

        MusicManager will work with any YouTube video audio.

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from abc import ABCMeta, abstractmethod
from mutagen import id3, MutagenError

import asyncio
import discord
import logging
import mutagen
import os
import queue
import time
import traceback


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


class YouTubeSong(Song):
    def __init__(self, yt_url, title, uploader, requestor,
                 channel, thumbnail=None):
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
        self.uploader = uploader
        self.thumbnail = thumbnail

    def announcement(self):
        # announcement = ("**Now playing:** *{title}* "
        #                 "[{min:0>2.0f}:{sec:0>2d}], "
        #                 "by {uploader}\n*Requested by {user}*").format(
        #     title=self.title,
        #     min=int(self.duration / 60),
        #     sec=int(self.duration % 60),
        #     uploader=self.uploader,
        #     user=self.requestor.name
        # )
        # return announcement

        em = discord.Embed(color=self.requestor.color)
        if (self.thumbnail is not None):
            # em.set_author(name=self.title, icon_url=self.thumbnail)
            em.set_author(name=self.title, url=self.url)
            em.set_thumbnail(url=self.thumbnail)
        else:
            em.set_author(name=self.title, url=self.url)
        em.add_field(name="Uploader", value=self.uploader, inline=True)
        em.add_field(
            name="Duration",
            value="[{min:0>2.0f}:{sec:0>2d}]".format(
                min=int(self.duration / 60),
                sec=int(self.duration % 60),
            ),
            inline=True)
        if (self.requestor.nick is None):
            em.set_footer(
                text="(Requested by {})".format(self.requestor.name),
                icon_url=self.requestor.avatar_url
            )
        else:
            em.set_footer(
                text="(Requested by {})".format(self.requestor.nick),
                icon_url=self.requestor.avatar_url
            )
        return em

    async def create_player(self, voice, after=None):
        self.logger.info("YouTubeSong: creating player")
        player = await voice.create_ytdl_player(self.url, after=after)
        self.duration = player.duration
        return player

"""
don't use this anymore
# class LocalSong(Song):
#     def __init__(self, title, name, requestor, channel):
#         super().__init__(title, requestor, channel)
#         self.path = None
#         ...
#
# class MP4Song(LocalSong):
#     ...
#     # Key fields here for artist, artwork, and title:
#     self.title = metadata['sonm'] or metadata['©nam']
#     self.artist = metadata['soar'] or metadata['aART'] or metadata['©ART']
#     self.thumbnail = metadata['covr']
#     # If you care:
#     genre = metadata['soal'] or metadata['©alb']
"""


class LocalSong(Song):
    def __init__(self, name, requestor, channel):
        self.path = "resources/music/{}".format(name)
        self.name = name
        self.url = self.name
        # To be overwritten later, hopefully
        self.thumbnail = None
        self.metadata = mutagen.File(self.path)
        self.duration = self.metadata.info.length

        # There are several file formats that don't even *have* a 'tags'
        # attribute; these should probably be identified, but having a
        # (sort of) catch-all exception is probably a good thing as well.
        try:
            if (type(self.metadata.tags) is mutagen.id3.ID3):
                # This should be able to take several audio formats,
                # namely AIFF, MP3, and True Audio. Maybe others?
                self.id3_init(name, requestor, channel)
            elif (type(self.metadata) is mutagen.mp4.MP4):
                # Used by both MP4 and M4A. Mutagen stresses primarily
                # MP4 compatibility with iTunes, so there may be issues
                # with some MP4 files.
                self.mp4_init(name, requestor, channel)
            # elif (type(self.metadata.tags) is mutagen._vorbis.VCommentDict):
            #     # Used by all of the mutagen types with 'vorbis' in their
            #     # name, and then some.
            #     self.do_whatever_vorbis_thing(name, requestor, channel)
            # elif (type(self.metadata.tags) is mutagen.apev2.APEv2):
            #     # Most everything else that even has tags uses these.
            #     self.do_whatever_apev2_thing(name, requestor, channel)
            else:
                raise MutagenError
        except AttributeError:
            raise MutagenError

        # mutagen_file = mutagen.File(self.path)
        # self.metadata = id3.ID3(self.path)
        # self.duration = mutagen_file.info.length

        # if (self.metadata.get('TIT2') is not None):
        #     title = str(self.metadata['TIT2'])
        # else:
        #     title = "{} (unknown title)".format(name)
        # super().__init__(title, requestor, channel)
        #
        # if (self.metadata.get('TPE1') is not None):
        #     self.artist = str(self.metadata['TPE1'])
        # elif (self.metadata.get('TOPE') is not None):
        #     self.artist = str(self.metadata['TOPE'])
        # elif (self.metadata.get('TCOM') is not None):
        #     self.artist = str(self.metadata['TCOM'])
        # else:
        #     self.artist = "Unknown Artist"

    def id3_init(self, name, requestor, channel):
        if (self.metadata.get('TIT2') is not None):
            title = str(self.metadata['TIT2'])
        else:
            title = "{} (unknown title)".format(name)
        super().__init__(title, requestor, channel)

        if (self.metadata.get('TPE1') is not None):
            self.artist = str(self.metadata['TPE1'])
        elif (self.metadata.get('TOPE') is not None):
            self.artist = str(self.metadata['TOPE'])
        elif (self.metadata.get('TCOM') is not None):
            self.artist = str(self.metadata['TCOM'])
        else:
            self.artist = "Unknown Artist"

    def mp4_init(self, name, requestor, channel):
        # Key fields here for artist, artwork, and title:
        # # self.title = metadata['sonm'] or metadata['©nam']
        # # self.artist = metadata['soar'] or metadata['aART'] or metadata['©ART']
        # # self.thumbnail = metadata['covr']
        # If you care:
        # # genre = metadata['soal'] or metadata['©alb']

        if (self.metadata.get('sonm') is not None):
            title = str(self.metadata['sonm'])
        elif (self.metadata.get('©nam') is not None):
            title = str(self.metadata['©nam'])
        else:
            title = "{} (unknown title)".format(name)
        super().__init__(title, requestor, channel)

        if (self.metadata.get('©ART') is not None):
            self.artist = str(self.metadata['©ART'])
        elif (self.metadata.get('soar') is not None):
            self.artist = str(self.metadata['soar'])
        elif (self.metadata.get('aART') is not None):
            self.artist = str(self.metadata['aART'])
        elif (self.metadata.get('\xa9wrt') is not None):
            self.artist = str(self.metadata['\xa9wrt'])
        else:
            self.artist = "Unknown Artist"

    # Currently only works with ID3 tags.
    async def save_artwork_url(self, client):
        if (type(self.metadata.tags) is mutagen.id3.ID3):
            await self.save_artwork_url_id3(client)
        elif (type(self.metadata) is mutagen.mp4.MP4):
            await self.save_artwork_url_mp4(client)
        else:
            self.thumbnail = None
            return None

    async def save_artwork_url_id3(self, client):
        if (self.metadata.get('APIC:') is None):
            self.logger.info("No album artwork found (no 'APIC:' key)")
            self.thumbnail = None
            return None
        elif (self.metadata.get('TXXX:art_url') is None):
            sent_file = client.imgur.upload(
                self.metadata['APIC:'].data, anon=False
            )
            url = sent_file['link']
            url_frame = id3.TXXX(
                encoding=3, desc=u'art_url', text=[url]
            )
            self.metadata.tags.add(url_frame)
            self.metadata.save()
            self.logger.info("Added '{}' to the ID3 tag 'TXXX:art_url'".format(
                url
            ))
            self.thumbnail = url
            return 0
        else:
            self.thumbnail = self.metadata['TXXX:art_url'].text[0]
            self.logger.info("Found existing artwork url: '{}'".format(
                self.thumbnail
            ))
            return 0

    async def save_artwork_url_mp4(self, client):
        if (self.metadata.get('covr') is None):
            self.logger.info("No album artwork found (no 'covr' key)")
            self.thumbnail = None
            return None
        elif (self.metadata.get('AUrl') is None):
            sent_file = client.imgur.upload(
                self.metadata['covr'][0], anon=False
            )
            url = sent_file['link']
            self.metadata['AUrl'] = url
            self.metadata.save()
            self.logger.info("Added '{}' to the MP4 tag 'AUrl'".format(
                url
            ))
            # self.logger.info("Uploaded '{}' to the MP4 tag 'AUrl'".format(
            #     url
            # ))
            self.thumbnail = url
            return 0
        else:
            self.thumbnail = self.metadata['AUrl'][0]
            self.logger.info("Found existing artwork url: '{}'".format(
                self.thumbnail
            ))
            return 0

    def announcement(self):
        # announcement = ("**Now playing:** *{title}* "
        #                 "[{min:0>2.0f}:{sec:0>2d}], "
        #                 "by {artist}\n*Requested by {user}*").format(
        #     title=self.title,
        #     min=int(self.duration / 60),
        #     sec=int(self.duration % 60),
        #     artist=self.artist,
        #     user=self.requestor.name
        # )
        # return announcement

        em = discord.Embed(color=self.requestor.color)
        if (self.thumbnail is not None):
            # em.set_author(name=self.title, icon_url=self.thumbnail)
            em.set_author(name=self.title)
            em.set_thumbnail(url=self.thumbnail)
        else:
            em.set_author(name=self.title)
        em.add_field(name="Artist", value=self.artist, inline=True)
        em.add_field(
            name="Duration",
            value="[{min:0>2.0f}:{sec:0>2d}]".format(
                min=int(self.duration / 60),
                sec=int(self.duration % 60),
            ),
            inline=True)
        em.set_footer(
            text="(Requested by {})".format(self.requestor.nick),
            icon_url=self.requestor.avatar_url
        )
        return em

    async def create_player(self, voice, after=None):
        self.logger.info("LocalSong: creating player")
        player = voice.create_ffmpeg_player(self.path, after=after)
        player.duration = int(self.duration)
        return player


class PlaylistEntry():
    def __init__(self, song):
        self.player = None
        self.announcement = None
        self.song = song

    async def load(self, voice, after=None):
        try:
            self.player = await self.song.create_player(voice, after=after)
        except:
            error_msg = "**ERROR:** Couldn't process request for {}".format(
                self.song.title
            )
            print(traceback.format_exc())
            return {'type': "error", 'response': error_msg}
        else:
            # self.announcement = self.song.announcement().format(
            #     min=int(self.player.duration / 60),
            #     sec=int(self.player.duration % 60),
            # )
            self.announcement = self.song.announcement()
            return {'type': "success", 'response': self.announcement}


class MusicManager():
    def __init__(self, core):
        self.core = core
        self.logger = logging.getLogger("core.MusicManager")
        discord.opus.load_opus("/usr/lib/x86_64-linux-gnu/libopus.so.0")
        self.start()

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
                self.current_song = self.playlist_queue.get()
                self.logger.debug("got next song")
                announce = await self.current_song.load(
                    voice=self.voice, after=self.advance_queue
                )
                if (type(announce['response']) is discord.embeds.Embed):
                    await self.core.send_message(
                        self.current_song.song.channel,
                        embed=announce['response']
                    )
                else:
                    await self.core.send_message(
                        self.current_song.song.channel, announce['response']
                    )
                if (announce['type'] == "error"):
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
            thumbnail=yt_embed['thumbnail']['url']
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

    async def local_add(self, name, requestor, channel):
        # music_library = os.listdir("resources/music")
        # if (name not in music_library):
        #     raise OSError("Song not found")
        if (not os.path.isfile("resources/music/{}".format(name))):
            raise FileNotFoundError("Song not found")
        try:
            song = LocalSong(name, requestor, channel)
        except MutagenError:
            self.logger.warning("Filetype of '{}' unsupported".format(name))
            raise OSError("Filetype of '{}' unsupported".format(name))
        else:
            await song.save_artwork_url(self.core)
            self.logger.info("local_add: Created song {}".format(song.title))
            playlist_entry = PlaylistEntry(song)
            self.logger.info(
                "local_add: Created playlist_entry {}".format(song.title)
            )
            self.playlist_queue.put(playlist_entry)
            self.logger.info(
                "local_add: Added playlist_entry {} to playlist_queue".format(
                    song.title)
            )
            response = ("Added *{title}*, by {uploader} to the playlist\n"
                        "*Requested by {user}*").format(
                title=song.title,
                uploader=song.artist,
                user=song.requestor.name
            )
            return {'type': "success", 'response': response}

    async def pause(self):
        if (self.is_connected() is False):
            return "**ERROR:** I'm not connected to voice right now."
        # elif (self.player.is_playing()):
        elif (self.is_active() is True):
            self.current_song.player.pause()
            return None
        else:
            return "**ERROR:** I'm not even playing anything right now smh"

    async def resume(self):
        if (self.is_connected() is False):
            return "**ERROR:** I'm not connected to voice right now."
        elif (self.is_active() is False):
            self.current_song.player.resume()
            return None

    async def skip(self):
        if (self.is_active()):
            self.logger.info("skipping song")
            self.current_song.player.stop()

    def list_library(self, album=""):
        try:
            library = os.listdir("resources/music/{}".format(album))
            self.logger.debug(library)
            return library
        except FileNotFoundError:
            self.logger.info("No album found for '{}'".format(album))
            return None

    async def list_playlist(self):
        # playlist = list(self.playlist_queue.queue)
        # playlist.insert(0, self.current_song)
        return self.current_song, list(self.playlist_queue.queue)

    def get_current_url(self):
        return self.current_song.song.url

    async def join_voice_channel(self, channel):
        # if (self.voice is not None and self.voice.is_connected()):
        if (self.voice is not None):
            await self.voice.move_to(channel)
            self.logger.info("Switched to vc #{}".format(channel.name))
        else:
            self.voice = await self.core.join_voice_channel(channel)
            self.logger.info("Connected to vc #{}".format(channel.name))
