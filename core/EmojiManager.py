"""
    Class Name : Emoji
    Class Version: 0.1

    Description:
        Attempts to manage custom emoji between servers.

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

import asyncio
import discord
import logging


class EmojiManager():
    def __init__(self, core):
        self.core = core
        self.logger = logging.getLogger("core.EmojiManager")

    def emoji(self, server, emoji_names):
        """
        Summary:
            Finds a custom emoji matching the first of a list of possible emoji
            names, and returns a string formatted with the snowflake for that
            server.

        Args:
            server (discord.Server): The server w/ emoji list.
            emoji_names (list(str)): An ordered list of emoji names to
                                     check for.

        Returns:
            (str):  Formatted emoji string, e.g. '<:my_b:232583716189241346>'
                    If the emoji isn't found, returns the first element of the
                    list.
        """
        if (server is None):
            self.logger.info("server is None")
            return "`:{}:`".format(emoji_names[0])
        self.logger.info("searching for :{}: in server {}".format(
            emoji_names[0], server.name
        ))
        for emoji_name in emoji_names:
            for emoji in server.emojis:
                self.logger.info("{} ?= {}".format(
                    repr(emoji.name), repr(emoji_name)
                ))
                if (emoji.name.lower() == emoji_name.lower()):
                    self.logger.debug(str(emoji))
                    return str(emoji)
        self.logger.info("no emoji found")
        return "`:{}:`".format(emoji_names[0])
