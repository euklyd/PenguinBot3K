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

    @command("^[Ss]tryker *(?:when he)? *\"(.*)\"$", access=-1, name='Stryker')
    async def stryker(self, msg, arguments):
        await self.send_message(msg.channel, "http://i.imgur.com/XpXoEDT.jpg")
        await self.send_message(
            msg.channel, "^ Stryker when he {}".format(msg.arguments[0]))
        await self.delete_message(msg)

    @command("^(?:[Nn]imious|<@!?163167281042423810>)$", access=100,
             name='Nimious')
    async def nimious(self, msg, arguments):
        ww_link = self.core.emoji.emoji(['ww_link_ugh'])
        bow = self.core.emoji.emoji(['bow'])
        bomb = self.core.emoji.emoji(['bomb'])
        danklink = self.core.emoji.emoji(['dank_link'])
        # dank_meme = ("Shut the fuck up <:ww_link_ugh:230236082892046337> Nimious <:ww_link_ugh:230236082892046337>. You're :zzz: fraudulent. You can't do anything besides <:bomb:230238267067334656> spam <:bow:230238510169325580>. That's what you have :cancer: Rosa :star2: as a :second_place: secondary :second_place: because she complements your :cartwheel: roll habits :cartwheel: you cocky :toilet: ass low level smasher :toilet:. Gtfoh bruh. Your entire play style is :regional_indicator_z: 2 buttons :b:. You give Link mains a bad name. The reason no one cheers for you is because of the :cheese: fraudulence :cheese: you show in your play. A real Link main like :muscle: Izaw :muscle: gets my respect.\n<:dank_link:230168078980218881> You literally aren't shit dude <:dank_link:230168078980218881>")
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
