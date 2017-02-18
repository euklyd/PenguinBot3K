"""
    Module Name : Config

    Description:
        Contains all global config options needed for the bot to run
        MAKE SURE TO CHANGE THE backdoor UNLESS YOU WANT YOUR BOT COMPROMISED

    Contributors:
        - Patrick Hennessy
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import discord
import logging

"""
    Profile settings

    Set by discord.Client.edit_profile()
"""
# Name the bot will refer to itself;
# will change name on server if it is not this
username = "My Penguin Bot"
avatar = "conf/king_dedede_icon.png"

"""
    Presence settings

    Set by discord.Client.change_presence()
"""
game = ""
# options are 'online', 'offline', 'idle', 'do_not_disturb', 'invisible'
status = discord.Status.online

"""
    Trigger

    Default command trigger. Messages that begin with any of these are
    considered commands
    If you want, you can set it to be a single string rather than a tuple.
"""
trigger = ('spikes ', 'Spikes ', '«', '»')

# Log level: https://docs.python.org/3/library/logging.html#logging-levels
log_level = logging.INFO
channel_logging = False

# Connector to use
connector = 'Discord'
# Set this to your bot's secret token.
connector_options = {
    'token': ''
}
# API tokens
api_tokens = {
    "steam":           "",
    "urbandictionary": "",
    "imgur":           "",
    "gliphy":          "",
    "github":          ""
}

# Ranks
ranks = {
    'guest': 50,
    'member': 100,
    'moderator': 150,
    'admin': 999
}

# Backdoor. If you want to override stuff, then set this to
# your personal user ID snowflake. This is dangerous, as
# whoever's ID this is will have full conrol over your bot.
backdoor = ''

# (public) Github stuff:
owner = "Euklyd / Popguin"
repo = "https://github.com/euklyd/PenguinBot3K/tree/discord.py"

# Names of plugins to be loaded. Will search the "plugin/" directory.
plugins = [
    'ACL',
    'Manage',
    'Macro',
    'Moderation',
    'Utility'
]

# imgur API
# You'll need an authorized application, which you can create yourself
# in about 5 minutes. This can then be connected to an existing imgur
# account (of yours).
# More info about all this can be found at http://api.imgur.com/
imgur_api = {
    'id': "YOUR IMGUR API ID",
    'secret': 'YOUR IMGUR API SECRET',
    'access': 'YOUR ACCESS TOKEN',
    'refresh': 'YOUR REFRESH TOKEN'
}

# Used for specifying things to happen on a designated server(s).
# Should be a string with the server ID.
# Can be a tuple of strings.
test_server = "No testing allowed"

# ID of default music voice channel. If this isn't a music bot, set it to None.
default_music_vc = None
