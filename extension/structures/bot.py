from discord.ext import commands, tasks

import typing
import os

from .database import models, DatabaseClient


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

        self.cached_servers = Cache()

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

    async def on_ready(self):
        print("I'm online!")

    async def on_message(self, message):
        server = await self.get_server(message.guild.id)

        if server.is_command_channel(message.channel.id):
            await self.process_commands(message)

    def new_task(self, coroutine):
        
