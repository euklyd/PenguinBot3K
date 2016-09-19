"""
    Class Name : Connector

    Description:
        Abstract class for which all backend connectors must derive

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from abc import *
import requests
import json
import time

class Connector():
    __metaclass__ = ABCMeta

    def __init__(self):
        self.last_request = time.time()

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def say(self, channel, message, mentions=[]):
        pass

    @abstractmethod
    def reply(self, user, channel, message):
        pass

    @abstractmethod
    def whisper(self, user, message):
        pass

    @abstractmethod
    def upload(self, channel, file):
        pass

    @abstractmethod
    def getUsers(self):
        pass

    @abstractmethod
    def getUser(self, userID):
        pass

    def request(self, method, request="?", headers=None, data={}, domain="discordapp.com", files={}):
        while(time.time() - self.last_request < 1):
            time.sleep(0.025)

        url = 'https://{}/api/{}'.format(domain, request)
        response = None

        try:
            if(method.lower() in ["post", "get", "delete", "head", "options", "put", "patch"]):
                self.lastRequest = time.time()
                if(method == "POST"):
                    response = requests.post(url, files=files, json=data, headers=headers)
                elif(method == "GET"):
                    response = requests.get(url, data, headers=headers)
                elif(method == "PUT"):
                    response = requests.put(url, data, headers=headers)
                elif(method == "DELETE"):
                    response = requests.delete(url, headers=headers)
                elif(method == "OPTIONS"):
                    response = requests.options(url)
                elif(method == "PATCH"):
                    response = requests.patch(url, data, headers=headers)
                elif(method == "HEAD"):
                    response = requests.head(url)
                elif(method == "UPDATE"):
                    response = requests.update(url, data, headers=headers)
            else:
                raise Exception("Invalid HTTP request method")

            if response.status_code not in range(200, 206):
                raise Exception("API responded with HTTP code  " + str(response.status_code) + "\n\n" + response.text)
            else:
                if response.text:
                    returnData = json.loads(response.text)
                    return returnData
                else:
                    return None
        except:
            pass
