from discord.ext import commands, tasks

import typing
import os

from .database import models, DatabaseClient

def is_duelist():
    async def check(ctx):
        return bool(ctx.player)
    return commands.check(check)

class Cache:
    def __init__(self):
        self._data = {}
        self.database_client = DatabaseClient(os.getenv("MONGODB_URL"))

    def add(self, reference: typing.Any, value: typing.Any) -> None:
        """
        Parameters
        ----------
        reference : typing.Any
        value : typing.Any
        """
        self._data[reference] = value

    def get(self, reference: typing.Any) -> typing.Any:
        """
        Parameters
        ----------
        reference : typing.Any

        Returns
        -------
        typing.Any

        Raises
        ------
        KeyError
        """
        return self._data[reference]


class Marjorie(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database_client = DatabaseClient(
            "mongodb+srv://Nium:123@cluster0-dhe4w.mongodb.net/test?retryWrites=true&w=majority"
        )

        self.cached_servers = Cache()
        self.cached_players = Cache()

    async def get_server(self, id: int) -> models.Server:
        """
        Parameters
        ----------
        id : int
            Discord ID of the server (guild).

        Returns
        -------
        models.Server
        """
        if type(id) is not int:
            raise TypeError("int expected in `id` parameter")

        try:
            return self.cached_servers.get(id)
        except KeyError:
            data = await self.database_client.get_server(id)

            if not data:
                data = models.Server.new(id)

                await self.database_client.new_server(data)

            return data

    async def get_player(self, id: int) -> models.Player:
        """
        Can be return `None`.

        Parameters
        ----------
        id : int
            Discord ID of the player.

        Returns
        -------
        models.Player
        """
        if type(id) is not int:
            raise TypeError("int expected in `id` parameter")

        try:
            return self.cached_players.get(id)
        except KeyError:
            data = await self.database_client.get_player(id)
            return data

    async def send(self, destiny, address: str, phs: dict, **kwargs):
        result = 
        await destiny.send(**kwargs)

    async def on_ready(self):
        print("I'm online!")

    async def process_commands(self, message, server):
        ctx = await self.get_context(message)

        if ctx.valid:
            player = await self.get_player(message.author.id)

            ctx.server = server
            ctx.player = player

            await self.invoke(ctx)

    async def on_message(self, message):
        if message.author.bot or message.is_system():
            return

        server = await self.get_server(message.guild.id)

        if server.is_command_channel(message.channel.id):
            await self.process_commands(message, server)
