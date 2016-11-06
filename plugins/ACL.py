"""
    Plugin Name : ACL
    Plugin Version : 2.0

    Description:
        Allows a chat interface to modifying user access

    Contributors:
        - Patrick Hennessy
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *
from peewee import *
from tabulate import tabulate

import random
import string

ACCESS = {
    "claim": -1,
    "deleteAccess": 500,
    "setAccess": 500,
    "ban": 900
}


class ACL(Plugin):
    @staticmethod
    def generate_key(length):
        return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(length))

    async def activate(self):
        if not self.core.ACL.owner:
            self.key = self.generate_key(32)
            self.logger.warning(
                "Claim this bot by typing '{} claim {}'".format(
                    self.core.config.trigger, self.key
                )
            )

    """I would put a docstring for this, but it's not supposed to be used by most users."""
    @command('^claim ([A-Za-z0-9]*)', access=ACCESS["claim"])
    async def claim(self, msg, arguments):
        if(arguments[0] == self.key):
            self.logger.critical('Bot has been claimed by: {} UID:{}'.format(
                msg.author.name, msg.author.id)
            )
            self.core.ACL.owner = msg.author.id ##FIX?
            await self.send_whisper(msg.author, 'You are now my owner! Wooo')

    @command("^whois <@!?([0-9]+)>", access=50)
    async def whois(self, msg, arguments):
        """`whois @<user>`: prints the access level of `<user>`, along with misc. information."""
        user = await self.get_user_info(arguments[0])
        access = self.core.ACL.getAccess(user.id)

        await self.send_message(
            msg.channel,
            "**Username:**\t`{}#{}`\nUser ID:\t`{}`\nAccess:\t`{}`".format(
                user.name, user.discriminator, user.id, access
                # user['user']['username'], user['user']['discriminator'],
                # user['user']['id'], access
            )
        )

    @command("^whoami", access=-1)
    async def whoami(self, msg, arguments):
        """`whoami`: prints your own access level."""
        access = self.core.ACL.getAccess(msg.author.id)

        await self.send_reply(msg, "\nUser ID\t`{}`\nAccess:\t`{}`".format(
            msg.author, access)
        )

    @command('^list users (-?[0-9]+)(?: ([0-9]+))?(?: ([0-9]+))?', access=100)
    async def get_some_users(self, msg, arguments):
        """`list users <access>`: list all users with the specified access level."""
        """
            More specifically, `access` != 0, then it gets a maximum of `limit`
            users with access equal to `access`, offset by `offset`.
        """
        access, limit, offset = arguments
        self.logger.info(arguments)

        table = []
        for user in self.core.ACL.query_users(access, limit, offset):
            table.append([user.id, user.cname, user.access])

        output = "**Users in my database: **\n\n"
        output += "`{}`".format(tabulate(table, headers=["ID", "Name", "Access"], tablefmt="psql", numalign="left"))

        await self.send_message(msg.channel, output)

    @command('^list users$', access=100)
    async def list_users(self, msg, arguments):
        """`list users`: list all users with non-default access levels."""

        table = []
        for user in self.core.ACL.query_users():
            table.append([user.id, user.cname, user.access])

        output = "**Users in my database: **\n\n"
        output += "`{}`".format(tabulate(table, headers=["ID", "Name", "Access"], tablefmt="psql", numalign="left"))

        await self.send_message(msg.channel, output)

    @command("^delete access <@!?([0-9]+)>", access=ACCESS["deleteAccess"])
    async def deleteAccess(self, msg, arguments):
        """`delete access @<user>`: deletes the access permissions of `<user>`."""
        requestor = msg.author.id
        target = arguments[0]

        if (requestor == target and requestor != self.core.config.backdoor):
            await self.send_reply(msg, "You cannot modify your own access")
            return

        # Check if requestor is allowed to do this
        if (self.core.ACL.getAccess(requestor) >= self.core.ACL.getAccess(target) or requestor != self.core.config.backdoor):
            user = await self.get_user_info(target)
            if (self.core.ACL.deleteUser(user) is True):
                await self.send_message(msg.channel, "Removed UID:`{}` from access list".format(target))
            else:
                await self.send_message(msg.channel, "Failed to remove UID:`{}` from access list".format(target))
        else:
            await self.send_reply(msg, "You cannot modify access of a user with more access")

    @command("^set access <@!?([0-9]+)> ([0-9]+)", access=ACCESS["setAccess"])
    async def setAccess(self, msg, arguments):
        """`set access @<user> <access>`: sets the access level of `<user>` to `<access>`."""
        requestor = msg.author.id
        target = arguments[0]

        # Check if requestor is allowed to do this
        if (requestor == target and requestor != self.core.config.backdoor):
            await self.send_reply(msg, "You cannot modify your own access")
            return

        if (self.core.ACL.getAccess(requestor) > self.core.ACL.getAccess(target) or requestor == self.core.config.backdoor):
            access = int(arguments[1])
            if (access >= 0 and access < 1000 or requestor == self.core.config.backdoor):
                # name = self.core.connection.getUser(target)["name"]
                user = await self.get_user_info(target)

                self.core.ACL.setAccess(user, access)
                await self.send_message(msg.channel, "Set **{}** UID:`{}` to access level: `{}`".format(user.name, target, access))
            else:
                await self.send_reply(msg, "Access must be between 0 and 999")

        else:
            await self.send_reply(msg, "You cannot modify access of a user with more access")
