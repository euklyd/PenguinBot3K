"""
    Plugin Name : Nimious
    Plugin Version : 0.1

    Description:
        Provides basic utility commands, e.g., coin flips.

    Contributors:
        - Popguin / Euklyd

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

"http://i.imgur.com/XpXoEDT.jpg"

from core.Plugin import Plugin
from core.Decorators import *
import logging

logger = logging.getLogger(__name__)


class Nimious(Plugin):
    def activate(self):
        pass

    @command("^[Ss]tryker *(?:when he)? *\"(.*)\"$", access=100)
    def stryker(self, msg):
        self.say(msg.channel, "http://i.imgur.com/XpXoEDT.jpg")
        self.say(msg.channel, "^ Stryker when he {}".format(msg.arguments[0]))
        self.delete_message(msg)

    @command("^(?:[Nn]imious)|(?:<@!?163167281042423810>)$")
    def nimious(self, msg):
        dank_meme = "Shut the fuck up :ww_link_ugh: Nimious :ww_link_ugh:. You're :zzz: fraudulent. You can't do anything besides :bomb~1: spam :bow~1:. That's what you have :cancer: Rosa :star2: as a :second_place: secondary :second_place: because she complements your :cartwheel: roll habits :cartwheel: you cocky :toilet: ass low level smasher :toilet:. Gtfoh bruh. Your entire play style is :regional_indicator_z: 2 buttons :b:. You give Link mains a bad name. The reason no one cheers for you is because of the :cheese: fraudulence :cheese: you show in your play. A real Link main like :muscle: Izaw :muscle: gets my respect.\n:dank_link: You literally aren't shit dude :dank_link:"
        self.say(msg.channel, dank_meme)
