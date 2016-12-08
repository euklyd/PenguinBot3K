"""
    Plugin Name : Voice
    Plugin Version : 2.0

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
from core.MusicManager import YouTubeSong, LocalSong

import asyncio
import discord
import glob
import os
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

    async def deactivate(self):
        await self.music_manager.close()

    @command("^vc joinvc <#([0-9]+)>$", access=ACCESS['conductor'],
             name='joinvc', doc_brief=("`vc joinvc <#channel_id>`: "
             "Joins the voice channel whose ID is `channel_id`."))
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
        except:
            await self.send_message(
                msg.channel,
                "**ERROR:** Something went terribly, terribly wrong "
                "in `joinvc()`"
            )

    @command("^vc library$", access=-1, name='library',
             doc_brief="`vc library`: List all songs stored in "
             "the local library (in a private message).")
    async def list_library(self, msg, arguments):
        library = self.music_manager.list_library()
        library.sort()
        self.logger.info(library)
        songs_reply = "**Unfiled Songs:**\n"
        albums_reply = "**Album Library:**\n"
        # songs = []
        # albums = []
        for item in library:
            if (os.path.isdir("resources/music/{}".format(item))):
                # albums.append(item)
                albums_reply += "`{}`\n".format(item)
            elif (item != "blank"):
                # songs.append(item)
                songs_reply += "`{}`\n".format(item)
        await self.send_message(msg.author, albums_reply)
        await self.send_message(msg.author, songs_reply)

    @command('^vc album "([^"]*)" ?(?:"([^"]*)")?$', access=-1, name='album',
             doc_brief='`vc album "album"`: List all songs stored in the '
             'album `album` in the local library (in a private message).',
             doc_detail='`vc album "album" `*`["term"]`*: List all songs '
             'stored in the album `album` (in a private message).\n\t'
             '[Optional]: If a second argument, `term`, is provided, only '
             'songs whose names contain `term` will be listed.')
    async def list_album(self, msg, arguments):
        songs = self.music_manager.list_library(arguments[0])
        if (arguments[1] is None):
            term = ""
        else:
            term = arguments[1]
        if (songs is not None):
            songs.sort()
            self.logger.debug(songs)
            self.logger.debug("search term: {}".format(term))
            reply = "**Music Library:**\n"
            for song in songs:
                if (term.lower() in song.lower()):
                    reply += "`{}`\n".format(song)
            reply += ('\n*(Use* `{trigger}vc queue "{album}" "<song>"` '
                      '*to play a song from "{album}")*'.format(
                        trigger=self.core.default_trigger,
                        album=arguments[0])
                      )
        else:
            reply = "**ERROR:** No album '{}' exists.".format(arguments[0])
        # await self.send_message(msg.author, reply)
        await self.send_message(msg.channel, reply)

    @command('^vc queue "([^"]*)"$', access=-1, name='local queue',
             doc_brief='`vc queue "song"`: Queue the audio from '
             'a local file named `song` (if it exists).')
    async def local_queue(self, msg, arguments):
        song_name = arguments[0]
        try:
            response = await self.music_manager.local_add(
                song_name, msg.author, msg.channel
            )
            response = response['response']
        except FileNotFoundError:
            response = ("Song not found; use `vc library` or `vc album` "
                        "to see available selections.")
        except OSError as e:
            response = (e)
        await self.send_message(msg.channel, response)
        await asyncio.sleep(1)
        await self.delete_message(msg)

    @command('^vc queue "([^"]*)" "([^"]*)"$', access=-1, name='local queue',
             doc_brief='`vc queue "album" "song"`: Queue the audio '
             'from a local file `song` in `album` (if it exists).')
    async def local_queue_album_song(self, msg, arguments):
        song_name = "{}/{}".format(arguments[0], arguments[1])
        try:
            response = await self.music_manager.local_add(
                song_name, msg.author, msg.channel
            )
            response = response['response']
        except FileNotFoundError:
            response = ("Song not found; use `vc library` or `vc album` "
                        "to see available selections.")
        except OSError:
            response = ("Filetype of song not supported.")
        await self.send_message(msg.channel, response)
        await asyncio.sleep(1)
        await self.delete_message(msg)

    @command('^vc queue album "([^"]*)" ?(?:"([^"]*)")?$',
             access=ACCESS['user'], name='local queue',
             doc_brief='`vc queue album "album"`: Queue all songs '
             'contained in the album `album`.',
             doc_detail='`vc queue album "album" ["pattern"]`: Queue all '
             'songs contained in the album `album` whose names match '
             '`pattern` (using standard Unix shell globbing).')
    async def local_queue_album_all(self, msg, arguments):
        album_name = arguments[0]
        try:
            if (arguments[1] is not None):
                songs = glob.glob1(
                    dirname="resources/music/{}".format(album_name),
                    pattern=arguments[1]
                )
                if (len(songs) == 0):
                    response = ("No songs found in album '{}' matching `{}`; "
                                "use `vc library` and `vc album` to see"
                                "available selections.")
                    await self.send_message(msg.channel, response)
                    return
            else:
                songs = os.listdir("resources/music/{}".format(album_name))
            self.logger.info(songs)
        except FileNotFoundError:
            response = ("Album not found; use `vc library` to see"
                        "available selections.")
            await self.send_message(msg.channel, response)
        else:
            for song_name in songs:
                song_name = "{}/{}".format(album_name, song_name)

                try:
                    response = await self.music_manager.local_add(
                        song_name, msg.author, msg.channel
                    )
                    response = response['response']
                except FileNotFoundError:
                    response = ("Song {} not found.".format(song_name))
                except OSError:
                    response = ("Filetype of {} not supported.".format(
                        song_name
                    ))
                await self.send_message(msg.channel, response)
                await asyncio.sleep(1)
            await self.delete_message(msg)

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

    def generate_playlist_line(self, song, top=False):
        """
            Helper function for the playlist commands.

            Takes a Song, and formats an entry for either
            YouTubeSong or LocalSong.
        """
        if (top is True):
            bullet = "🔊"
        else:
            bullet = "-"
        if (type(song) is YouTubeSong):
            entry = ("{bullet} ***{song}***, by {uploader} "
                     "(requested by {requestor})\n").format(
                bullet=bullet,
                song=song.title,
                uploader=song.uploader,
                requestor=song.requestor
            )
        else:
            entry = ("{bullet} ***{song}***, by {uploader} "
                     "(requested by {artist})\n").format(
                bullet=bullet,
                song=song.title,
                artist=song.artist,
                requestor=song.requestor
            )
        return entry

    @command("^vc playlist$", access=-1, name='playlist',
             doc_brief="`vc playlist`: Show current playlist.")
    async def show_playlist(self, msg, arguments):
        current_song, playlist = await self.music_manager.list_playlist()
        reply = "**Current YouTube Playlist:**\n"
        if (current_song is not None):
            reply += self.generate_playlist_line(current_song.song, top=True)
            for entry in playlist:
                reply += self.generate_playlist_line(entry.song)
                # if (len(reply) > 1500):
                #     await self.send_message(msg.channel, reply)
                #     reply = ""
        else:
            reply += "Playlist is empty!"
        if (len(reply) > 2000):
            reply = "**Next Ten Songs in YouTube Playlist:**\n"
            if (current_song is not None):
                reply += self.generate_playlist_line(current_song.song,
                                                     top=True)
            for i in range(0, 10):
                try:
                    reply += self.generate_playlist_line(playlist[i].song)
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
