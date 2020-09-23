from discord.ext import commands

import typing
import os
import asyncio

from .database import models, DatabaseClient
from extension.structures import errors, utils


DEFAULT_LANGUAGE = "english"


def is_duelist():
    async def check(ctx):
        if ctx.player:
            return True
        raise errors.IsNotDuelistError()
    return commands.check(check)


def not_dueling():
    async def check(ctx):
        return True
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


class MarjorieContext(commands.Context):
    @property
    def language(self) -> str:
        """
        Retorna a lingua que está sendoe usada no contexto.
        """
        try:
            return self.server.language
        except AttributeError:
            if self.player:
                return self.player.language

            return DEFAULT_LANGUAGE

    @property
    def or_separator(self) -> str:
        if self.language == "pt-br":
            return "ou"
        elif self.language == "english":
            return "or"
        else:
            return '?'

    def get_sample_address(self, address):
        command_name = self.command.name

        if self.command.parent:
            command_name += '.' + self.command.parent.name

        return utils.join_address(command_name, address)

    async def send(self, address: str, root="Commands",):
        if root == "Commands":
            address = self.get_sample_address(address)
        else:
            address = utils.join_address(root, address)

        address = utils.join_address(address, self.language)


class Marjorie(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database_client = DatabaseClient(os.getenv("MONGODB_URL"))

        self.cached_servers = Cache()
        self.cached_players = Cache()

        self._tasks = []
        self.loop.create_task(self._task_reader())

    async def _task_reader(self):
        while True:
            if not self._tasks:
                await asyncio.sleep(10)

            for index, task in enumerate(self._tasks):
                if task.done():
                    task = self._tasks.pop(index)
                    task.print_stack()

                    break

            await asyncio.sleep(.5)

    def create_task(self, coroutine):
        task = self.loop.create_task(coroutine)
        self._tasks.append(task)

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
                self.cached_servers.add(id, data)

                await self.database_client.new_server(data)

                return data

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

            self.cached_players.add(id, data)

            return data

    async def send(self, destiny, address: str, phs: dict, **kwargs):
        """
        Envia o resultado formato de `address` com `phs` para `destiny`.
        """
        result = utils.get_address_result(address, phs)
        result = result.format(**phs)
        await destiny.send(result, **kwargs)

    async def on_ready(self):
        print("I'm online!")

    async def process_commands(self, message, server):
        ctx = await self.get_context(message, cls=MarjorieContext)

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

    async def on_command_error(self, ctx, error):
        if isinstance(error, errors.IsNotDuelistError):
            await ctx.send("Not duelist")

        else:
            raise error
