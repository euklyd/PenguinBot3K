"""
    Plugin Name : Nimious
    Plugin Version : 3.0

    Description:
        Provides "fun" user-specific commands. Requested by Nimious,
        hence the name. Generally unlisted.

    Contributors:
        - Popguin / Euklyd

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *
import logging

logger = logging.getLogger(__name__)


class Nimious(Plugin):
    async def activate(self):
        pass

    @command("^[Ss]tryker *(?:when he)? *(.*)$", access=-1, name='Stryker')
    async def stryker(self, msg, arguments):
        await self.send_message(msg.channel, "http://i.imgur.com/XpXoEDT.jpg")
        if (arguments[0] is not None):
            await self.send_message(
                msg.channel,
                "^ Stryker when he {}".format(arguments[0])
            )
        await self.delete_message(msg)

    @command("^(?:[Nn]imious|<@!?163167281042423810>)$", access=100,
             name='Nimious')
    async def nimious(self, msg, arguments):
        ww_link = self.core.emoji.any_emoji(['ww_link_ugh'])
        bow = self.core.emoji.any_emoji(['bow'])
        bomb = self.core.emoji.any_emoji(['bomb'])
        danklink = self.core.emoji.any_emoji(['dank_link'])
        dank_meme = (
            "Shut the fuck up {ww} Nimious {ww}. You're 💤 fraudulent. "
            "You can't do anything besides {bomb} spam {bow}. That's why you "
            "have ♋ Rosa 🌟 as a 🥈 secondary 🥈 because she complements your "
            "🤸 roll habits 🤸 you cocky 🚽 ass low level smasher 🚽. "
            "Gtfoh bruh. Your entire play style is 🇿 2 buttons 🅱. "
            "You give Link mains a bad name. The reason no one cheers for you "
            "is because of the 🧀 fraudulence 🧀 you show in your play. "
            "A real Link main like 💪 Izaw 💪 gets my respect.\n"
            "{dank_link} You literally aren't shit dude {dank_link}".format(
                ww=ww_link,
                bomb=bomb,
                bow=bow,
                dank_link=danklink
            )
        )
        await self.send_message(msg.channel, dank_meme)
        await self.delete_message(msg)
