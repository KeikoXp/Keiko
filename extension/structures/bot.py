from discord.ext import commands
import aiohttp
import discord

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



class MarjorieContext(commands.Context):
    @property
    def language(self) -> str:
        """
        Retorna a lingua que está sendo usada no contexto.
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

    async def raw_send(self, *args, **kwargs):
        return await super().send(*args, **kwargs)

    async def send(self, address: str, root="Commands", **phs):
        if root == "Commands":
            address = self.get_sample_address(address)

        address = utils.join_address(root, address)
        address = utils.join_address(address, self.language)

        result = utils.get_address_result(address, phs)

        return await super().send(result)


class Marjorie(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database_client = DatabaseClient(os.getenv("MONGODB_URL"))

        self.session = aiohttp.ClientSession()

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

    async def get_server(self, guild) -> models.Server:
        """
        Parametros
        ----------
        guild : typing.Union[discord.Guild, int]
            Discord ID do servidor ou o próprio objeto dela.

        Retorno
        -------
        models.Server
        """
        if type(guild) is discord.Guild:
            guild = guild.id

        return await self.database_client.get_server(guild)

    async def get_player(self, id: int) -> models.Player:
        """
        Pode retornar `None`.

        Parametros
        ----------
        id : int
            Discord ID do jogador.

        Retorno
        -------
        models.Player
        """
        return await self.database_client.get_player(id)

    async def new_duelist(self, id: int, class_):
        """
        Cria um novo duelista.

        Parametros
        ----------
        id : int
            Discord ID do jogador.
        class_ : duel.classes.Class
            A classe do jogador.

        Raises
        ------
        ValueError
            O duelista já está registrado.
        """
        # Não é necessário verificar o tipo dos parametros pois o método
        # abaixo utiliza os mesmos tipos e já faz essa verificação.
        player = models.Player.new_duelist(id, class_)

        await self.database_client.new_player(player)

        # Se o jogador já estiver registrado, o método acima irá causar
        # um erro finalizando este método e não irá colocar `Player` em
        # cache.

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
        
        if not ctx.valid:
            return

        player = await self.get_player(message.author.id)

        ctx.server = server
        ctx.player = player

        await self.invoke(ctx)

    async def on_message(self, message):
        if message.author.bot or message.is_system():
            return

        server = await self.get_server(message.guild.id)
        if server and server.is_command_channel(message.channel.id):
            await self.process_commands(message, server)

    async def on_command_error(self, ctx, error):
        if isinstance(error, errors.IsNotDuelistError):
            await ctx.send(root="Errors", address="IsNotDuelistError")

        else:
            raise error
