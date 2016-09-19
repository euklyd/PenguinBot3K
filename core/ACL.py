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

class ACLUser(Model):
    id      = IntegerField(primary_key=True)
    cname   = CharField(max_length=128, default="")
    access  = IntegerField(default=0, constraints=[Check('access >= 0'), Check('access <= 1000') ])
    owner   = BooleanField(default=False)

class ACL():
    def __init__(self):
        self.database = Database(databaseName="databases/ACL.db")
        self.database.addTable(ACLUser)

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
    def owner(self, uid):
        """
            Summary:
                Sets the bot owner

            Args:
                uid (str): ID of the target user

            Returns:
                None
        """
        user, created = self.database.ACLUser.get_or_create(id=uid)

        if(created):
            user.id = uid
            user.access = 1000
            user.owner = True
            user.save()
        else:
            user.owner = True
            user.save()

    def setAccess(self, uid, access, cname=""):
        """
            Summary:
                Sets the database access for a specific user

            Args:
                uid (str): ID of the target user

            Returns:
                (Bool): Successful or Not
        """
        # Check if trying to change owner
        if(self.getOwner == uid):
            return False

        # Set user access
        user, created = self.database.ACLUser.get_or_create(id=uid)

        if(created):
            user.id = uid
            user.access = access
            user.cname = cname
            user.save()
        else:
            user.access = access
            user.cname = cname
            user.save()

        return True

    def getAccess(self, uid):
        """
            Summary:
                Gets the database access for the specified user

            Args:
                uid (str): ID of the target user

            Returns:
                (Int): Access level of the target user, or -1 if not found
        """
        try:
            user = ACLUser.get(id=uid)
            return user.access
        except:
            return -1

    def query_users(self, access, limit=0, offset=0):
        """
            Summary:
                Gets all the users the bot knows about

            Args:
                None

            Returns:
                (List): User objects defined above
        """
        try:
            users = ACLUser.select().where(ACLUser.access == access).order_by(ACLUser.access.desc()).limit(limit).offset(offset)
            return users
        except:
            return -1

    def deleteUser(self, uid):
        """
            Summary:
                Deletes a user from the ACL database

            Args:
                uid (str): ID of the target user

            Returns:
                (Bool): Successful or Not
        """
        try:
            user = self.database.ACLUser.get(id=uid)
            if(user):
                user.delete_instance()
                return True
            else:
                return False
        except:
            return False
