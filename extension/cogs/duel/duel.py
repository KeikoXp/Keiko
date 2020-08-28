from discord.ext import commands

import asyncio


class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.queue = list()
        self.queue_task = bot.create_task(self.queue_selector())

    async def match(self, player_one, player_two):
        pass

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


def setup(bot):
    cog = Duel(bot)
    bot.add_cog(cog)
