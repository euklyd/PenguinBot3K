"""
    Plugin Name : HaruFE
    Plugin Version : 0.1

    Description:
        Interacts with Harudoku's HaruFE game.

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

logger = logging.getLogger(__name__)

path = "resources/harufe/{}"


class User:
    def __init__(self, id):
        self.id = id
        self.wishlist = {}
        self.offerings = {}


class Item:
    def __init__(self):
        self.name
        self.aliases       # e.g., ["starlight ring", "starlitering"]
        self.sellers = {}  # dict of id:User


class Marketplace:
    def __init__(self):
        self.users = {}  # id:       User
        self.db    = {}  # itemName: Item

    def populateDB(self):
        pass
        # with etc as etc:
        #     json stuff etc.

    def populateUsers(self):
        pass
        # with etc as etc:
        #     json stuff etc.


class HaruFE(Plugin):
    async def activate(self):
        self.balances = {}
        try:
            with open(path.format("haru_channels.json"), 'r') as chfile:
                self.harufe_channels = json.load(chfile)
        except FileNotFoundError:
            self.harufe_channels = []
        try:
            with open(path.format("alms.json"), 'r') as goldfile:
                self.balances = json.load(goldfile)
        except FileNotFoundError:
            self.balances = {}

    @command("^preach <#(\d+)> every (\d+ (?:sec|min)) for (\d+ (?:min|hours?))",
             access=500, name='preach',
             doc_brief="`preach <#channel> every <time sec/min> for "
             "<time min/hours>`")
    async def preach(self, msg, arguments):
        theses = ["No theses found."]
        try:
            with open(path.format("95-theses.json"), 'r') as thesesfile:
                theses = json.load(thesesfile)
                theses = list(theses.values())
        except FileNotFoundError:
            theses = ["No theses found."]
        period = 60
        duration = 3600
        if ("min" in arguments[1]):
            period = int(arguments[1].split(' ')[0]) * 60
        else:
            period = int(arguments[1].split(' ')[0])
        if ("min" in arguments[2]):
            duration = int(arguments[2].split(' ')[0]) * 60
        else:
            duration = int(arguments[2].split(' ')[0]) * 60 * 60
        repetitions = duration/period
        while repetitions > 0:
            repetitions -= 1
            await self.send_message(msg.channel_mentions[0],
                                    random.choice(theses))
            await asyncio.sleep(period)
        await self.send_message(msg.channel_mentions[0], random.choice(theses))
        await self.send_message(msg.channel_mentions[0], "Done preaching.")

    @filter("^~[Gg][Ii][Vv][Ee] <@!?[\d]*>$", name='reform',
            server=['190782508105728000', '244381473610792961', '328399532368855041'])
    async def reformation(self, msg, arguments):
        if (msg.channel.id not in self.harufe_channels):
            self.logger.warning("quit from bad cid")
            return
        if (msg.mentions[0].id != self.core.user.id):
            self.logger.warning("quit from bad mention")
            return
        harubot = await self.core.wait_for_message(
            timeout=3600,
            channel=msg.channel,
            content="Alright. Would you like to give that person `gold`, "
                    "an `item`, `silver mark`s, `gold mark`s, or `nothing`?"
        )
        if (harubot is None):
            self.logger.warning("quit from timeout 1")
            return
        harubot = harubot.author
        resp = await self.core.wait_for_message(
            timeout=3600,
            author=msg.author,
            channel=msg.channel,
        )
        if (resp is None):
            self.logger.warning("quit from timeout 2")
            return
        elif (resp.content.lower() != "gold"):
            self.logger.warning("quit from non-gold")
            return
        resp = await self.core.wait_for_message(
            timeout=3600,
            author=harubot,
            channel=msg.channel,
            check=lambda m: "How much gold would you like to give Martin Luther?" in m.content
        )
        if (resp is None):
            self.logger.warning("quit from timeout 3")
            return
        await self.send_message(
            msg.channel,
            "I am ready to accept your deposit, my child."
        )
        resp = await self.core.wait_for_message(
            timeout=3600,
            author=msg.author,
            channel=msg.channel,
        )
        if (resp is None):
            self.logger.warning("quit from timeout 4")
            return
        gold = resp.content
        self.logger.info("Got {} gold".format(gold))

        # FIXME: catch things like "You don't have that much gold.
        # Run this command again when you feel like donating gold you have."
        # and "Negative gold doesn't work", etc.
        await self.core.wait_for_message(
            timeout=3600,
            author=harubot,
            channel=msg.channel,
            content="You give Martin Luther {} gold.".format(gold)
        )
        if (resp is None):
            self.logger.warning("quit from timeout 5")
            return
        if (msg.author.id in self.balances):
            self.balances[msg.author.id] += int(gold)
        else:
            self.balances[msg.author.id] = int(gold)
        with open(path.format("alms.json"), 'w+') as goldfile:
            self.logger.info("updated balances")
            json.dump(self.balances, goldfile, indent=2)
        await self.send_message(
            msg.channel,
            "I have successfully received your deposit of {} gold. "
            "Your new balance is {}.\n"
            "Viva la Reformation!".format(gold, self.balances[msg.author.id])
        )

    @command("^withdraw (\d+)",
             access=-1, name='withdraw',
             doc_brief="`withdraw <gold>`: withdraw <gold> from your deposit.")
    async def withdraw(self, msg, arguments):
        if (msg.channel.id not in self.harufe_channels):
            self.logger.warning("quit from bad cid")
            return
        gold = int(arguments[0])
        if (msg.author.id not in self.balances):
            await self.send_message(
                msg.channel,
                "My child, you don't seem to have supported the Reformation 💔"
            )
            return
        if (gold > self.balances[msg.author.id]):
            await self.send_message(
                msg.channel,
                "My child, you only have {} gold stored with us.".format(
                    self.balances[msg.author.id]
                )
            )
            return
        await self.send_message(
            msg.channel, "~give {}".format(msg.author.mention)
        )
        harubot = await self.core.wait_for_message(
            timeout=3600,
            channel=msg.channel,
            content="Alright. Would you like to give that person `gold`, "
                    "an `item`, `silver mark`s, `gold mark`s, or `nothing`?"
        )
        if (harubot is None):
            self.logger.warning("quit from timeout 1")
            return
        harubot = harubot.author
        await asyncio.sleep(0.5)
        await self.send_message(msg.channel, "gold")
        resp = await self.core.wait_for_message(
            timeout=3600,
            author=harubot,
            channel=msg.channel,
            check=lambda m: "How much gold would you like to give" in m.content
        )
        if (resp is None):
            self.logger.warning("quit from timeout 2")
            return
        await asyncio.sleep(0.5)
        await self.send_message(msg.channel, str(gold))
        resp = await self.core.wait_for_message(
            timeout=3600,
            author=harubot,
            channel=msg.channel,
            check=lambda m: "{} gold.".format(gold) in m.content
        )
        if (resp is None):
            self.logger.warning("quit from timeout 3")
            return
        self.balances[msg.author.id] -= gold
        with open(path.format("alms.json"), 'w+') as goldfile:
            self.logger.info("updated balances")
            json.dump(self.balances, goldfile, indent=2)
        await asyncio.sleep(0.5)
        await self.send_message(
            msg.channel,
            "My gratitude for standing with us against the corrupt church, "
            "child."
        )

    @command("^haruch (add|rm|list)",
             access=500, name='haruch',
             doc_brief="`haruch <add|rm>`: designate a channel as a place "
             "for HaruFE, or not.")
    async def haruchannel(self, msg, arguments):
        if arguments[0].lower() == 'add':
            if msg.channel.id in self.harufe_channels:
                await self.send_message(
                    msg.channel,
                    "{} is already a HaruFE channel.".format(msg.channel.id)
                )
                return
            self.harufe_channels.append(msg.channel.id)
        elif arguments[0].lower() == 'rm':
            if msg.channel.id not in self.harufe_channels:
                await self.send_message(
                    msg.channel,
                    "{} isn't a HaruFE channel.".format(msg.channel.id)
                )
                return
            self.harufe_channels.remove(msg.channel.id)
        elif arguments[0].lower() == 'list' or arguments[0] == '':
            reply = "**HaruFE Channels:**\n"
            for ch_id in self.harufe_channels:
                reply += "<#{}>\n".format(ch_id)
            await self.send_message(msg.channel, reply)
            return
        else:
            return
        with open(path.format("haru_channels.json"), 'w+') as chfile:
            self.logger.info("updated harufe channels")
            json.dump(self.harufe_channels, chfile, indent=2)
        await self.send_message(msg.channel, "Updated channel list.")

    @command("^ingotratio (\d+) ?(\d+)?$", name='ingotratio', access=-1,
             doc_brief="`ingotratio <gold> (<gold per silver>)`: Converts an "
             "amount of gold to an optimal ratio of gold and silver for pure "
             "ingot gacha. Gold : silver exchange rate defaults to 600:1.")
    async def ingotratio(self, msg, arguments):
        gold = int(arguments[0])
        gold_per_sil = 600
        if arguments[1] is not None:
            gold_per_sil = int(arguments[1])

        gold_per_ingot = 4000 + 800
        sil_per_ingot = 5
        total_cost_per_ingot = gold_per_ingot + sil_per_ingot * gold_per_sil

        n_ingots = gold // total_cost_per_ingot
        gold_out = n_ingots * gold_per_ingot + gold % total_cost_per_ingot
        sil_out = 5 * n_ingots
        reply = (
            "Gold: `{}`, silver marks: `{}`, for `{}` Pure Ingots @ {} gold "
            "per silver mark.".format(gold_out, sil_out, n_ingots, gold_per_sil)
        )
        await self.send_message(
            msg.channel,
            reply
        )
