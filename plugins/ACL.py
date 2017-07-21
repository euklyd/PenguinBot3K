"""
    Plugin Name : ACL
    Plugin Version : 3.0

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

import discord
import random
import string

ACCESS = {
    "claim": -1,
    "queryAccess": 100,
    "setAccess": 500,
    "ban": 900,
    "roleAccess": 999
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

    # I would put a doc_brief or doc_detail for this, but it's not supposed
    # to be used by most users.
    @command('^claim ([A-Za-z0-9]*)', access=ACCESS["claim"], name='claim')
    async def claim(self, msg, arguments):
        if(arguments[0] == self.key):
            self.logger.critical('Bot has been claimed by: {} UID:{}'.format(
                msg.author.name, msg.author.id)
            )
            self.core.ACL.owner = msg.author.id  ##FIX?
            await self.send_whisper(msg.author, 'You are now my owner! Wooo')

    @command("^whois <@!?([0-9]+)>", access=50, name='whois',
             doc_brief="`whois @<user>`: prints the access level of `<user>`, "
             "along with misc. information.")
    async def whois(self, msg, arguments):
        # user = await self.get_user_info(arguments[0])
        user = msg.mentions[0]
        access = self.core.ACL.getAccess(user.id)
        em = discord.Embed(color=user.color)
        em.set_author(
            name="{}#{}".format(user.name, user.discriminator),
            icon_url=user.avatar_url
        )
        em.add_field(name="ID", value=user.id)
        em.add_field(name="User Access", value=access)

        # await self.send_message(
        #     msg.channel,
        #     "**Username:**\t`{}#{}`\nUser ID:\t`{}`\nAccess:\t`{}`".format(
        #         user.name, user.discriminator, user.id, access
        #     )
        # )
        await self.send_message(msg.channel, embed=em)

    @command("^whoami", access=-1, name='whoami',
             doc_brief="`whoami`: prints your own access level.")
    async def whoami(self, msg, arguments):
        access = self.core.ACL.getAccess(msg.author.id)

        await self.send_reply(msg, "\nUser ID\t`{}`\nAccess:\t`{}`".format(
            msg.author, access)
        )

    @command('^list users (-?[0-9]+)(?: ([0-9]+))?(?: ([0-9]+))?$',
             access=ACCESS['queryAccess'], name='list users',
             doc_brief="`list users <access>`: list all users with the "
             "specified access level.",
             doc_detail="`list users <access>`: list all users with the "
             "specified access level.\n"
             "More specifically, if `access` != 0, then a maximum of `limit` "
             "users with access equal to `access`, offset by `offset`, are "
             "returned.")
    async def get_some_users(self, msg, arguments):
        access, limit, offset = arguments
        self.logger.info(arguments)

        table = []
        for user in self.core.ACL.query_users(access, limit, offset):
            table.append([user.id, user.cname, user.access])

        output = "**Users in my database: **\n\n"
        output += "`{}`".format(
            tabulate(
                table,
                headers=["ID", "Name", "Access"],
                tablefmt="psql",
                numalign="left"
            )
        )

        await self.send_message(msg.channel, output)

    @command('^list users$', access=ACCESS['queryAccess'], name='list users',
             doc_brief="`list users`: list all users with non-default access "
             "levels.")
    async def list_users(self, msg, arguments):
        table = []
        for user in self.core.ACL.query_users():
            table.append([user.id, user.cname, user.access])

        output = "**Users in my database: **\n\n"
        output += "`{}`".format(
            tabulate(
                table,
                headers=["ID", "Name", "Access"],
                tablefmt="psql",
                numalign="left"
            )
        )

        await self.send_message(msg.channel, output)

    @command("^delete access <@!?([0-9]+)>", access=ACCESS['setAccess'],
             name='delete access',
             doc_brief=("`delete access @<user>`: deletes the access "
             "permissions of `<user>`."))
    async def deleteAccess(self, msg, arguments):
        requestor = msg.author.id
        target = arguments[0]

        if (requestor == target and requestor != self.core.config.backdoor):
            await self.send_reply(msg, "You cannot modify your own access")
            return

        # Check if requestor is allowed to do this
        if (self.core.ACL.getAccess(requestor) >= self.core.ACL.getAccess(target) or
                requestor != self.core.config.backdoor):
            # user = await self.get_user_info(target)
            user = msg.mentions[0]
            if (self.core.ACL.deleteUser(user) is True):
                await self.send_message(
                    msg.channel,
                    "Removed UID:`{}` from access list".format(target)
                )
            else:
                await self.send_message(
                    msg.channel,
                    "Failed to remove UID:`{}` from access list".format(target)
                )
        else:
            await self.send_reply(
                msg,
                "You cannot modify access of a user with more access"
            )

    @command("^set access <@!?([0-9]+)> ([0-9]+)", access=ACCESS["setAccess"],
             name='set access',
             doc_brief=("`set access @<user> <access>`: sets the access level "
             "of `<user>` to `<access>`."))
    async def setAccess(self, msg, arguments):
        requestor = msg.author.id
        target = arguments[0]

        # Check if requestor is allowed to do this
        if (requestor == target and requestor != self.core.config.backdoor):
            await self.send_reply(msg, "You cannot modify your own access")
            return

        if (self.core.ACL.getAccess(requestor) > self.core.ACL.getAccess(target) or
                requestor == self.core.config.backdoor):
            access = int(arguments[1])
            if (access >= 0 and access < 1000 or
                    requestor == self.core.config.backdoor):
                # user = await self.get_user_info(target)
                user = msg.mentions[0]

                self.core.ACL.setAccess(user, access)
                await self.send_message(
                    msg.channel,
                    "Set **{}** UID:`{}` to access level: `{}`".format(
                        user.name, target, access
                    )
                )
            else:
                await self.send_reply(msg, "Access must be between 0 and 999")

        else:
            await self.send_reply(
                msg,
                "You cannot modify access of a user with more access"
            )

    @command("^set role access <@&([0-9]+)> ([A-Za-z0-9]+) ([0-9]+)$",
             access=ACCESS['roleAccess'], name='set role access',
             doc_brief="`set role access @<role> <plugin> <access>`: "
             "sets the access level of `<role>` to `<access>` for the "
             "specified <plugin>.")
    async def set_role_access(self, msg, arguments):
        role_id = arguments[0]
        plugin  = arguments[1]
        access  = int(arguments[2])
        # self.logger.info("{}, {}, {}".format(role_id, plugin, access))
        # self.logger.info(self.core.plugin.plugins.keys())
        if (plugin in self.core.plugin.plugins):
            reply = self.core.ACL.set_role_access(role_id, plugin, access)
            if (reply is None):
                await self.send_message(
                    msg.channel,
                    "Set `{role}` to access level `{access}` "
                    "for plugin '**{plugin}**'".format(
                        role=role_id, plugin=plugin, access=access)
                )
            else:
                await self.send_message(msg.channel, reply)
        else:
            await self.send_message(msg.channel, "No such plugin!")

    @command("^delete role access <@&([0-9]+)> ([A-Za-z0-9]+)$",
             access=ACCESS['roleAccess'], name='delete role access',
             doc_brief="`delete role access @<role> <plugin>`: removes the "
             "access level of `<role>` for the specified <plugin>.")
    async def delete_role_access(self, msg, arguments):
        role_id = arguments[0]
        plugin  = arguments[1]
        try:
            self.core.ACL.delete_role_access(role_id, plugin)
            reply = ("Deleted access of `{role}` for plugin "
                     "'**{plugin}**'").format(role=role_id, plugin=plugin)
        except KeyError as e:
            reply = str(e).strip('"\'')
        await self.send_message(msg.channel, reply)

    @command("^access (?:<@!?([0-9]+)>|<@&([0-9]+)>|([0-9]+))$",
             access=ACCESS['queryAccess'], name='access',
             doc_brief="`access @<user/role>`: Returns the access level of "
             "the specified user or role.")
    async def access(self, msg, arguments):
        if (arguments[0] is not None):
            # it's a user
            self.whois(msg, [arguments[0]])
            return
        elif (arguments[1] is not None):
            # it's a role mention
            # access_map = self.core.ACL.get_role_accesses(arguments[1])
            if (len(msg.role_mentions) > 0):
                role = msg.role_mentions[0]
            else:
                role = self.core.get_role_info(msg.raw_role_mentions[0], msg.server)
            access_map = self.core.ACL.get_role_accesses(role)
        elif (arguments[2] is not None):
            # it's a role id
            role = self.core.get_role_info(arguments[2], msg.server)
            access_map = self.core.ACL.get_role_accesses(role)
        else:
            # it went wrong
            self.logger.warning(
                "something went wrong with command '{}'".format(msg.content))
            return
        self.logger.info(access_map)
        if access_map is not None:
            reply = access_map
        else:
            reply = "No permissions set for {}.".format(role)
        # em = discord.Embed(color=user.color)
        # em.set_author(
        #     name="{}#{}".format(user.name, user.discriminator),
        #     icon_url=user.avatar_url
        # )
        # em.add_field(name="ID", value=user.id)
        # em.add_field(name="User Access", value=access)
        # for plugin in access_map:
        #     reply +=
        await self.send_message(msg.channel, reply)
