from discord.ext import commands
import discord

import asyncio

from extension import structures


class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.queue = list()
        self.queue_task = bot.create_task(self.queue_selector())

        self.duels = []

    async def match(self, player_one: int, player_two: int):
        player_one = self.bot.get_user(player_one)
        if not player_one:
            return self.queue.append(player_two)

        player_two = self.bot.get_user(player_two)
        if not player_two:
            return self.queue.append(player_one.id)

        start_match = await self.confirm_match(player_one, player_two)
        if start_match:
            self.bot.duels.start(player_one.id)
            self.bot.duels.start(player_two.id)

            player_one_data = await self.bot.get_player(player_one)
            player_two_data = await self.bot.get_player(player_two)

            player_one = structures.duel.MortalPlayer(player_one_data, player_one)
            player_two = structures.duel.MortalPlayer(player_two_data, player_two)
            # cria as estruturas para que os duelistas possam duelar.

            players = (player_one, player_two)

            env = structures.duel.Environment(players, self.bot)
            self.bot.envs.append(env)
            # guardar o ambiente em que o duelo está acontencendo é
            # de extrema importância para que seja mais fácil de analisar
            # uma partida em andamento sem ter que finaliza-lá.

            try:
                await env.start()
            except Exception as error:
                # Pode acontecer de uma pessoa fechar a DM durante o
                # duelo, se isso acontecer, um erro é gerado.

                base_address = "Commands.duel.canceled-match."
                try:
                    address = base_address + player_one.language
                    await self.bot.send(player_one, address)
                except Forbidden:
                    pass

                try:
                    address = base_address + player_two.language
                    await self.bot.send(player_two, address)
                except Forbidden:
                    pass

                raise error
            finally:
                self.bot.duels.stop(player_one.id)
                self.bot.duels.stop(player_two.id)

    async def queue_selector(self):
        while True:
            try:
                player_one = self.queue.pop()
            except IndexError:
                await asyncio.sleep(10)
                continue

            if not self.queue:
                self.queue.append(player_one)
                await asyncio.sleep(10)
                continue

            for index, player_two in enumerate(self.queue):
                # FIXME
                # Pode acontecer da lista mudar de tamanho, se isso
                # acontecer, um erro é gerado.
                # Isso acontece apenas se um item é inserido em um index
                # em que a iteração já tenha passado.
                # No nosso caso, acontecerá quando um jogador premium
                # entrar na fila, pois ele é inserido no começo da fila.
                player_two = self.queue.pop(index)

                coroutine = self.match(player_one, player_two)
                self.bot.loop.create_task(coroutine) # self.bot.new_task(coroutine)
                # É extramemente necessário criar uma task, além de não
                # interromper a execução do código, fará com que erros
                # gerados na função também não interrompão o código.

            await sleep(1)

    @structures.bot.is_duelist()
    @commands.command(name="duel")
    async def duel_command(self, ctx):
        pass


def setup(bot):
    cog = Duel(bot)
    bot.add_cog(cog)
