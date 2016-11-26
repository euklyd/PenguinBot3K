"""
    Plugin Name : Pokemon
    Plugin Version : 0.1

    Description:
        Gives Pokemon-related commands

    Contributors:
        - Euklyd / Popguin

    License:
        Arcbot is free software: you can redistribute it and/or modify it
        under the terms of the GNU General Public License v3; as published
        by the Free Software Foundation
"""

from core.Plugin import Plugin
from core.Decorators import *

import asyncio
import pyqrcode
import random
import string

ACCESS = {
}


class Pokemon(Plugin):
    async def activate(self):
        pass

    @command("^poke [Qq][Rr]", access=-1, name='QR Code',
             doc_brief="`poke qr`: generates a random QR code.")
    async def qr_code(self, msg, arguments):
        qr_filename = "resources/pokemon_code.png"
        try:
            qr_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))  # noqa: E501
            qr_code = pyqrcode.create(qr_str)
            qr_code.png(qr_filename, scale=7)
        except:
            await self.send_message(
                msg.channel,
                "**ERROR:** Could not generate QR code."
            )
            return
        try:
            await self.send_message(msg.channel, "Generated a QR code:")
            with open(qr_filename, 'rb') as qr_file:
                await self.send_file(
                    msg.channel,
                    qr_file,
                    filename="pokemon_qr_code.png"
                )
        except:
            await self.send_message(
                msg.channel,
                "**ERROR:** Could not upload QR code."
            )
            return
