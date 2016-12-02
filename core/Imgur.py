"""
    Class Name : Imgur

    Description:
        Interfaces with the imgur API.

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from imgurpython import ImgurClient

import base64


class Imgur(ImgurClient):
    def __init__(self, core):
        self.core = core
        # self.id = core.config.imgur['id']
        # self.secret = core.config.imgur['secret']
        # self.refresh = core.config.imgur['refresh']
        # self.access = core.config.imgur['access']
        client_id = core.config.imgur['id']
        client_secret = core.config.imgur['secret']
        refresh_token = core.config.imgur['refresh']
        access_token = core.config.imgur['access']

        # client = ImgurClient(client_id, client_secret, access_token, refresh_token)
        super().__init__(client_id, client_secret, access_token, refresh_token)

    # stolen from https://github.com/Imgur/imgurpython
    def upload(self, bytes, config=None, anon=True):
        """
            Takes a file-like object (bytes) and uploads to imgur
        """
        if not config:
            config = dict()

        contents = bytes
        b64 = base64.b64encode(contents)
        data = {
            'image': b64,
            'type': 'base64',
        }
        data.update({meta: config[meta] for meta in set(self.allowed_image_fields).intersection(config.keys())})

        return self.make_request('POST', 'upload', data, anon)
