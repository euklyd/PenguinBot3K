"""
    Plugin Name : Utility
    Plugin Version : 3.0

    Description:
        Provides basic utility commands, e.g., random selectors
        and user info.

    Contributors:
        - Popguin / Euklyd

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *
import discord
import io
import json
import logging
import os
from PIL import Image
import random
import re
import requests
import string

logger = logging.getLogger(__name__)

resource_path = "resources/{}"


class Utility(Plugin):
    async def activate(self):
        pass

    @command("^flip$", access=-1, name='flip',
             doc_brief="`flip`: Flips a coin that will come up either heads "
             "or tails. Images of many types of coins are included.")
    async def flip(self, msg, arguments):
        coin = random.randint(0, 10)
        user = msg.server.get_member(self.core.user.id)
        em = discord.Embed(color=user.color)
        em.set_footer(
            text="",
            icon_url=user.avatar_url
        )
        if (coin % 2 == 0):
            em.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/a/a0/2006_Quarter_Proof.png")  # noqa E501
        else:
            tails = random.randint(0, 10)
            if (tails % 10 == 0):
                em.set_thumbnail(url="http://i.imgur.com/jiLvSSL.png")
            else:
                em.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/4/4e/COBREcentavosecuador2000-2.png")  # noqa E501
        await self.send_message(msg.channel, embed=em)

    @command("^pick(?:[- ]one)? (.*)", access=-1, name='pick',
             doc_brief="`pick one <list of items>`: Selects one item out of "
             "a list of space-separated items.")
    async def pick_one(self, msg, arguments):
        items = arguments[0].split(' ')
        choice = random.choice(items)
        await self.send_message(
            msg.channel,
            "<@!{}>, your selection is **{}**!".format(msg.author.id, choice)
        )

    @command("^(?:r|roll) ([0-9]{1,4})d([0-9]{1,4})", access=-1, name='roll',
             doc_brief="`r XdY`: Rolls X Y-sided dice.")
    async def roll(self, msg, arguments):
        roll = 0
        for i in range(0, int(arguments[0])):
            roll += random.randint(1, int(arguments[1]))
        await self.send_message(
            msg.channel,
            "{user}, you rolled `{x}d{y}` and got **{roll}**".format(
                user=msg.author.mention,
                x=arguments[0], y=arguments[1],
                roll=roll)
        )

    @command("^(?:er|eroll) (?P<dice>[+-]\d{1,3}d\d{1,3}(?:[+-]\d{1,3}d\d{1,3}){0,8})(?:(?P<mod>[+-]\d{1,3}))?(?: # ?(?P<comment>.*))?",
             access=-1, name='eroll',
             doc_brief="`er <dice expression>`: extended roll")
    async def eroll(self, msg, arguments):
        self.logger.info(arguments)
        # dice = re.split('+|-', arguments['dice'])
        splits = re.split('(\+|\-)', arguments[0])
        self.logger.info('splits: {}'.format(splits))
        splits = [e for e in splits if e != '']
        if splits[0] != '+' and splits[0] != '-':
            dice = splits[::2]
            signs = ['+'] + splits[1::2]
        else:
            dice = splits[1::2]
            signs = splits[::2]
        self.logger.info('dice:  {}'.format(dice))
        self.logger.info('signs: {}'.format(signs))
        adds = []
        for a in signs:
            if a == '+':
                adds.append(1)
            else:
                adds.append(-1)
        results = []
        for d in dice:
            die = d.split('d')
            die[0], die[1] = int(die[0]), int(die[1])
            res = []
            for i in range(0, die[0]):
                roll = random.randint(1, die[1])
                res.append(roll)
            results.append(res)
        self.logger.info('results: {}'.format(results))
        result = 0
        rmsg = ""
        for a, r in zip(adds, results):
            dmsg = ""
            for d in r:
                result += a*d
                if dmsg == "":
                    dmsg = str(d)
                else:
                    dmsg += " + {}".format(d)
            if (a == -1):
                rmsg += " - ({})".format(dmsg)
            elif (rmsg != ""):
                rmsg += " + ({})".format(dmsg)
            else:
                rmsg = "({})".format(dmsg)
        if (arguments[1] is not None):
            if (arguments[1][0] == '+'):
                mod = int(arguments[1].strip('+-'))
                rmsg += " + {}".format(mod)
            else:
                mod = -1 * int(arguments[1].strip('+-'))
                rmsg += " - {}".format(-1 * mod)
            result += mod
        rmsg += "\n**= {}**".format(result)
        # rmsg += "\n({})".format(arguments['comment'])
        if (arguments[2] is not None):
            rmsg += "\n*({})*".format(arguments[2])
        await self.send_message(msg.channel, rmsg)

    @command("^shuffle (.*)", access=-1, name='shuffle',
             doc_brief="`shuffle <list of items>`: Returns the list in a "
             "random order.")
    async def shuffle(self, msg, arguments):
        items = arguments[0].split(' ')
        random.shuffle(items)
        await self.send_message(msg.channel, items)

    @command("^avatar <@!?([0-9]*)>$", access=-1, name='avatar',
             doc_brief="`avatar @<user>`: posts a link to `<user>`'s avatar")
    async def get_avatar(self, msg, arguments):
        """`avatar @<user>`: posts a link to `<user>`'s avatar"""
        if (len(msg.mentions) == 0):
            # msg.mentions will be empty if the mentioned user isn't a member
            # of the server
            user = await self.core.get_user_info(arguments[0])
        else:
            user = msg.mentions[0]
        self.logger.info(user.avatar)
        self.logger.info(user.avatar_url)
        if (type(user) is discord.User):
            # discord.Server.get_member() returns None if the specified user
            # isn't a part of that server.
            em = discord.Embed()
            nick = user.name
        else:
            em = discord.Embed(color=user.color)
            if (user.nick is None):
                nick = user.name
            else:
                nick = user.nick
        em.set_author(
            name="{}#{}".format(user.name, user.discriminator),
            url=user.avatar_url
        )
        em.set_thumbnail(url=user.avatar_url)
        if (".gif" in user.avatar_url):
            nitro = "Yes"
        else:
            nitro = "maybe? maybe not? 👀"
        em.add_field(name="Nickname", value=nick)
        em.add_field(name="Nitro", value=nitro)
        em.add_field(name="URL", value="([long link, click here!]({}))".format(user.avatar_url), inline=False)
        await self.send_message(msg.channel, embed=em)

    @command("^info <@!?([0-9]*)>$", access=-1, name='info',
             doc_brief="`info @<user>`: Gets assorted info about the "
             "specified <user>.")
    async def get_info(self, msg, arguments):
        if (len(msg.mentions) == 0):
            # msg.mentions will be empty if the mentioned user isn't a member
            # of the server
            user = await self.core.get_user_info(arguments[0])
        else:
            user = msg.mentions[0]
        if (type(user) == discord.Member):
            # If the user isn't on this server, then they're a discord.User
            # rather than discord.Member, and so are missing a lot of fields.
            em = discord.Embed(color=user.color)
            nick = user.nick
            color = "{} (`{}`)".format(user.color.to_tuple(), user.color)
            status = user.status
            game = user.game
            role = user.top_role
            n_roles = " [{}]".format(len(user.roles))
            em.set_footer(text="Joined on {}".format(user.joined_at))
        else:
            em = discord.Embed()
            nick = "None"
            color = "None"
            status = "None"
            role = "None"
            n_roles = ""
            game = "None"
            em.set_footer(text="Created on {} (not a member of this "
                               "server)".format(user.created_at))
        em.set_author(
            name="{}#{}".format(user.name, user.discriminator),
            icon_url=user.avatar_url
        )
        em.add_field(name="Nickname", value=nick, inline=True)
        em.add_field(name="ID",       value="`{}`".format(user.id))
        em.add_field(name="Color",    value=color)  # inline is True by default
        em.add_field(name="Status",   value=status)
        em.add_field(name=("Top Role" + n_roles), value=role)
        em.add_field(name="Game",     value=game)
        em.set_thumbnail(url=user.avatar_url)

        await self.send_message(msg.channel, embed=em)

    @command("^(?:info|emoji) <(a?):(.*):(\d*)>$", access=-1, name="emoji info",
             doc_brief="`emoji`: Gets info about the specified emoji")
    async def emoji_info(self, msg, arguments):
        em_name = arguments[1]
        em_id = arguments[2]
        emoji = self.core.emoji.exact_emoji(em_name, em_id)
        url = self.core.emoji.gif_url(em_id) if arguments[0] == 'a' else self.core.emoji.url(em_id)

        em = discord.Embed(
            color=msg.server.get_member(self.core.user.id).color
        )
        em.set_thumbnail(url=url)

        if emoji is not None:
            em.set_author(
                name="<{}:{}:{}>".format(arguments[0], emoji.name, emoji.id),
                icon_url=emoji.server.icon_url
            )
            em.set_footer(text="Created on {}".format(emoji.created_at))
            em.add_field(name="Server", value=emoji.server.name)
            em.add_field(name="ID",     value="`{}`".format(em_id))
            em.add_field(name="URL",    value="[{}]({})".format(em_name, url))
            if len(emoji.roles) > 0:
                em.add_field(name="Role restricted?", value=True)
            else:
                em.add_field(name="Role restricted?", value=False)
        else:
            em.set_author(
                name="<{}:{}:{}>".format(arguments[0], em_name, em_id),
                icon_url="https://i.imgur.com/5UKaW9f.jpg"
            )
            em.set_footer(text="No shared server; info is limited")
            em.add_field(name="Server", value="???")
            em.add_field(name="ID",     value="`{}`".format(em_id))
            em.add_field(name="URL",    value="[{}]({})".format(em_name, url))

        await self.send_message(msg.channel, embed=em)

    @command("^(?:bigmoji )?<(a?):(\w*):(\d+)>$", access=-1, name='bigmoji',
             doc_brief="`bigmoji <emoji>`: Biggifies <emoji>.")
    async def bigmoji(self, msg, arguments):
        em_url = self.core.emoji.url(arguments[2])
        ext = 'png'
        if arguments[0] == 'a':
            em_url = self.core.emoji.gif_url(arguments[2])
            ext = 'gif'
        dest = "/tmp/{arg[1]}_{arg[2]}-{usr}.{ext}".format(
            arg=arguments, usr=msg.author.nick, ext=ext
        )
        with open(dest, 'wb') as imgfile:
            req = requests.get(em_url)
            imgfile.write(req.content)
        await self.send_file(
            msg.channel,
            dest,
        )
        os.remove(dest)
        await self.delete_message(msg)

    @command("^server(:? info)?$", access=100, name='info',
             doc_brief="`server info`: Gets assorted info about the "
             "current server.")
    async def get_server_info(self, msg, arguments):
        user = msg.server.get_member(self.core.user.id)
        server = msg.server

        owner = server.owner

        region_dict = {
            discord.ServerRegion.us_west: "🇺🇸",
            discord.ServerRegion.us_east: "🇺🇸",
            discord.ServerRegion.us_central: "🇺🇸",
            discord.ServerRegion.eu_west: "🇪🇺",
            discord.ServerRegion.eu_central: "🇪🇺",
            discord.ServerRegion.singapore: "🇸🇬",
            discord.ServerRegion.london: "🇬🇧",
            discord.ServerRegion.sydney: "🇦🇺",
            discord.ServerRegion.amsterdam: "🇳🇱",
            discord.ServerRegion.frankfurt: "🇩🇪",
            discord.ServerRegion.brazil: "🇧🇷",
            discord.ServerRegion.vip_us_east: "🇺🇸⭐",
            discord.ServerRegion.vip_us_west: "🇺🇸⭐",
            discord.ServerRegion.vip_amsterdam: "🇳🇱⭐",
        }

        em = discord.Embed(color=user.color)
        em.set_author(
            name="{} {}".format(server.name, region_dict[server.region]),
            icon_url=server.icon_url
        )
        em.set_thumbnail(url=server.icon_url)

        em.add_field(name="Region",    value=str(server.region), inline=True)
        em.add_field(name="ID",        value="`{}`".format(server.id))
        em.add_field(name="# members", value=server.member_count)
        em.add_field(name="# roles",   value=str(len(server.roles)))
        em.add_field(name="Top Role",  value="<@&{}>".format(
            server.role_hierarchy[0].id)
        )
        em.add_field(name="Owner",     value=server.owner.mention)
        if (server.default_channel is None):
            default_ch = None
        else:
            default_ch = "<#{}>".format(server.default_channel.id)
        em.add_field(name="Default channel", value=default_ch)
        # em.add_field(name="Default voice",     value=???)
        em.add_field(name="Verification",    value=server.verification_level)

        em.set_footer(
            text="Created on {}".format(server.created_at),
            icon_url=user.avatar_url
        )

        await self.send_message(msg.channel, embed=em)

    def santashuffle(self, orig):
        rand_list = orig[:]
        random.shuffle(rand_list)
        offset = [rand_list[-1]] + rand_list[:-1]
        return rand_list, offset

    @command("^secretsanta(?: <@!?[0-9]*>)+$", access=100, name='secretsanta',
             doc_brief="`secretsanta @user1 @user2 ...`: Creates a secret "
             "santa chain with each user in the list, and DMs each the name "
             "of their recipient.")
    async def secretsanta(self, msg, arguments):
        santas, offset = self.santashuffle(msg.mentions)
        for santa, recipient in zip(santas, offset):
            await self.send_whisper(
                santa,
                "Your secret santa is {}#{}".format(
                    recipient.name, recipient.discriminator
                )
            )
        await self.send_message(msg.channel, "Santas sent!")

    def decode_steg_url(self, url):
        resp = requests.get(url)
        img = Image.open(io.BytesIO(resp.content))
        pixelMap = img.load()
        pos = 0
        msgLen = ""
        msg = ""
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                if pos < 8:
                    msgLen += chr(pixelMap[i, j][3] + ord(' '))
                    pos += 1
                elif pos < int(msgLen)+8:
                    msg += chr(pixelMap[i, j][3] + ord(' '))
                    pos += 1
        return msg

    def encode_steg_url(self, url, secret):
        resp = requests.get(url)
        im = Image.open(io.BytesIO(resp.content))
        # secret = "popguin was here, toemonkey is a loser"
        sizeSecret = "{:0>8}{}".format(len(secret), secret)
        pixelMap = im.load()

        img = Image.new(im.mode, im.size)
        pixelsNew = img.load()
        pos = 0
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                if pos < len(sizeSecret):
                    pixelMap[i, j] = (
                        pixelMap[i, j][0],
                        pixelMap[i, j][1],
                        pixelMap[i, j][2],
                        ord(sizeSecret[pos]) - ord(' ')
                    )
                    pos += 1
                pixelsNew[i, j] = pixelMap[i, j]
        # img.show()
        ofile = "/tmp/steg_{}.png".format(secret)
        img.save(ofile)
        print('encoded "{}" into {}'.format(secret, ofile))

    @command("^decode <:(\w*):(\d+)>$", access=-1, name='decode',
             doc_brief="`decode :emoji:`: Reads the message hidden in "
             "`:emoji:`, if it exists.")
    async def decode(self, msg, arguments):
        plaintext = self.decode_steg_url(self.core.emoji.url(arguments[1]))
        await self.send_message(
            msg.channel,
            "<:{}:{}> `{}`".format(arguments[0], arguments[1], plaintext)
        )

    @command("^encode <:(\w*):(\d+)> ([\w ,.!?;:]+)$", access=1000,
             name='encode',
             doc_brief="`encode :emoji: secret message here`: Hides `secret "
             "message here` inside `:emoji:`.")
    async def encode(self, msg, arguments):
        secret = arguments[2]
        old_emoji = self.core.emoji.exact_emoji(arguments[0], arguments[1])
        ofile = "/tmp/steg_{}.png".format(secret)
        self.encode_steg_url(self.core.emoji.url(arguments[1]), secret)
        with open(ofile, 'rb') as emBytes:
            em = await self.core.create_custom_emoji(
                msg.server,
                name=arguments[0],
                image=emBytes.read()
            )
        if old_emoji.server != msg.server:
            await self.send_file(
                msg.server,
                ofile,
                content="{} is not on this server; have an upload instead".format(old_emoji)
            )
            os.remove(ofile)
            return
        os.remove(ofile)
        await self.core.delete_custom_emoji(old_emoji)
        await self.send_message(
            msg.channel,
            "Encoded `{}` into {}; old version is:\n{}".format(secret, em, self.core.emoji.url(arguments[1]))
        )

    @command("^(?:smallcaps|sc) (.*)$", access=-1, name='smallcaps',
             doc_brief="`smallcaps <msg>` Converts <msg> into sᴍᴀʟʟ ᴄᴀᴘs")
    async def smallcaps(self, msg, arguments):
        alphabet = {
            'a': 'ᴀ',
            'b': 'ʙ',
            'c': 'ᴄ',
            'd': 'ᴅ',
            'e': 'ᴇ',
            'f': 'ғ',
            'g': 'ɢ',
            'h': 'ʜ',
            'i': 'ɪ',
            'j': 'ᴊ',
            'k': 'ᴋ',
            'l': 'ʟ',
            'm': 'ᴍ',
            'n': 'ɴ',
            'o': 'ᴏ',
            'p': 'ᴘ',
            'q': 'ǫ',
            'r': 'ʀ',
            's': 's',
            't': 'ᴛ',
            'u': 'ᴜ',
            'v': 'ᴠ',
            'w': 'ᴡ',
            'x': 'x',
            'y': 'ʏ',
            'z': 'ᴢ'
        }
        reply = ''
        for c in arguments[0]:
            reply += alphabet.get(c, c)
        await self.send_message(msg.channel, reply)

    @command("^tagteam( list)?( games)?$", name='tagteam')
    async def tagteam_gamelist(self, msg, arguments):
        games = {}
        with open(resource_path.format("tagteam-chapters.json"), 'r') as listfile:
            games = json.load(listfile)
        names = list(games.keys())
        done = [name for name in names if len(games[name]) > 0]
        todo = [name for name in names if name not in done]
        done.sort(key=fe_split)
        todo.sort(key=fe_split)
        reply = "**Games implemented:** {}\n**To-do:** {}".format(
            ', '.join(done),
            ', '.join(todo)
        )
        await self.send_message(msg.channel, reply)

    @command("^tagteam (\w+) (<@!?\d+> ?)+", name='tagteam',
             doc_brief="`tagteam <game> <@player1> <@player2> ...`: "
             "randomly split up the chapters of the FE game of your choice "
             "between the mentioned players.")
    async def tagteam(self, msg, arguments):
        game = arguments[0].upper()
        games = {}
        with open(resource_path.format("tagteam-chapters.json"), 'r') as listfile:
            games = json.load(listfile)
        if game not in games:
            keys = list(games.keys())
            keys.sort()
            reply = (
                "{} not in the list of games; the games you can select are:"
                "\n{}"
            ).format(game, ', '.join(keys))
            await self.send_message(msg.channel, reply)
            return
        chapters = games[game]
        if len(chapters) == 0:
            await self.send_message(
                msg.channel,
                "{} hasn't been implemented yet, try another game".format(game)
            )
            return
        picks = {}
        team = msg.mentions
        random.shuffle(team)
        for player in team:
            picks[player] = []
        random.shuffle(chapters)
        i = 0
        for chapter in chapters:
            picks[team[i]].append(chapter)
            i = (i+1) % len(team)
        reply = "Randomized Chapter List:\n\n"
        for player in team:
            reply += "**{} ({})**\n".format(player, len(picks[player]))
            picks[player].sort(key=ch_split)
            for chapter in picks[player]:
                reply += "- {}\n".format(chapter)
            reply += "\n"
        await self.send_message(msg.channel, reply)

    @command("^embed <#(\d+)> ```(?:json\n)?(.*)``` ?(.*)?", name='embed', access=700,
             doc_brief="`embed #channel ```<json>````: Given an embed JSON "
             "from https://leovoel.github.io/embed-visualizer/, embed it in "
             "#channel as a Discord Embed.")
    async def embed(self, msg, arguments):
        try:
            data = json.loads(arguments[1])
            if 'timestamp' in data:
                data.pop('timestamp')
            if 'image' in data and arguments[2] != '':
                data.pop('image')
            em = discord.Embed.from_data(data)
            em.set_footer(
                text=msg.author.nick,
                icon_url=msg.author.avatar_url
            )
            if arguments[2] != '':
                em.set_image(arguments[2])
        except Exception as e:
            await self.send_message(msg.channel, "Error: {}".format(e))
            return
        await self.send_message(msg.channel_mentions[0], embed=em)


def fe_split(fe):
    if not fe.startswith('FE'):
        return 100 + ord(fe[0])
    letters = tuple(string.ascii_letters)
    fe = fe.split('FE')[1]
    while(fe.endswith(letters)):
        fe = fe[:-1]
    return int(fe)


def ch_split(ch):
    if not ch.startswith('Chapter'):
        return [100, ch]
    ch = ch.split('Chapter ')[1]
    ch = ch.split(':')[0]
    ch = ch.split('/')[0]
    m = re.compile('(\d+)([a-zA-Z]*)')
    ch = list(m.match(ch).groups())
    ch[0] = int(ch[0])
    return ch
