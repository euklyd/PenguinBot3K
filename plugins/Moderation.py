"""
    Plugin Name : Moderation
    Plugin Version : 0.1

    Description:
        Provides some moderation commands, e.g., banning users.

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *

import random
import string

ACCESS = {
    "claim": -1,
    "deleteAccess": 500,
    "setAccess": 500,
    "ban": 900
}


class Moderation(Plugin):
    def activate(self):
        self.saved_messages = []
        pass


    @command("^ban <@!?([0-9]+)>", access=ACCESS["ban"])
    def server_ban(self, msg):
        user = msg.arguments[0]
        server = self.core.connection.get_server(msg)['id']
        if (int(self.core.ACL.getAccess(msg.sender)) <= int(self.core.ACL.getAccess(user))):
            self.say(msg.channel, "Nice try, <@!{}>. <@!100165629373337600> has been notified.")
            return
        else:
            mtg_banish = {'grip_of_desolation': "http://i.imgur.com/vgbxZsH.png",
                          'vindicate': "http://i.imgur.com/ZVXcGmu.jpg"}
            banish = mtg_banish[random.choice(list(mtg_banish.keys()))]

            #self.ban_user(server, user)
            self.core.connection.ban_user(server, user, delete_msgs=0)
            self.say(msg.channel, banish)
            self.say(msg.channel, "Geeeeeet **dunked on**, <@!{}>!".format(user))


    @command("^nuke <@!?([0-9]+)> ([1-7])$", access=ACCESS["ban"])
    def nuke(self, msg):
        user = msg.arguments[0]
        delete_days = int(msg.arguments[1])
        server = self.core.connection.get_server(msg)['id']
        if (int(self.core.ACL.getAccess(msg.sender)) <= int(self.core.ACL.getAccess(user))):
            self.say(msg.channel, "Nice try, <@!{}>. <@!100165629373337600> has been notified.")
            return
        else:
            mtg_banish = {'merciless_eviction': "http://i.imgur.com/wm9hbzi.png"}
            banish = mtg_banish[random.choice(list(mtg_banish.keys()))]

            self.core.connection.ban_user(server, user, delete_msgs=delete_days)
            self.say(msg.channel, banish)
            self.say(msg.channel, "Geeeeeet **dunked on**, <@!{}>!".format(user))


    @command("^push ([0-9]*)$")
    def push_messages(self, msg):
        pass

    @command("^pop <#([0-9]*)>$")
    def pop_messages(self, msg):
        # clear the stack
        self.saved_messages = []

    @command("^pop$")
    def pop_clear(self, msg):
        # clear the stack
        self.saved_messages = []
