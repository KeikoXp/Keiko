from discord.ext import commands
from discord import errors as discord_errors

import asyncio
import traceback

from extension import structures
from extension.structures import utils


class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.queue = list()
        self.queue_task = bot.loop.create_task(self.queue_selector())

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

                # TODO
                # Verificar se o erro foi porque alguém fechou a DM.
                traceback.print_exc()

                base_address = "Commands.duel.canceled-match."
                try:
                    address = base_address + player_one.language
                    await self.bot.send(player_one, address)
                except discord_errors.Forbidden:
                    pass

                try:
                    address = base_address + player_two.language
                    await self.bot.send(player_two, address)
                except discord_errors.Forbidden:
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
                player_two = self.queue[index]

                if player_one and player_two:
                    # TODO
                    # Criar um verificador pra ver se um duelo entre
                    # ambos players é justa.
                    self.queue.pop(index) # Retira o `player_two` da
                    # queue.

                    coroutine = self.match(player_one, player_two)
                    task = self.bot.loop.create_task(coroutine)
                    self.bot.tasks.append(task)
                    # É extramemente necessário criar uma task, além de não
                    # interromper a execução do código, fará com que erros
                    # gerados na função também não interrompão o código.

                    break

            await sleep(1)

    @structures.bot.is_duelist()
    #@structures.bot.not_dueling()
    @commands.command(name="duel")
    async def duel_command(self, ctx):
        if ctx.author.id in self.queue:
            return await ctx.send(travel="in-queue")

        try:
            await ctx.send(destiny=ctx.author, travel="put-in-queue")
        except discord_errors.Forbidden:
            await ctx.send(root="Errors", travel="Forbidden.DM-CLOSED")
        else:
            if ctx.player.premium:
                self.queue.insert(0, ctx.author.id)
            else:
                self.queue.append(ctx.author.id)

            if ctx.guild:
                await ctx.message.add_reaction('✅')

    @commands.command(name="start")
    async def start_command(self, ctx):
        messages = utils.get_address_result("Others.change-language-message")
        await ctx.send('\n'.join(messages))

        await asyncio.sleep(10)

        notes = utils.get_address_result("Commands.start.note")
        for text in utils.get_address_result("Commands.start.phrases"):
            text = text[ctx.server.language]
            text += "\n\n" + notes[ctx.server.language]

            try:
                await message.edit(content=text)
            except:
                message = await ctx.send(text)
            finally:
                await message.add_reaction('➡️')

            def check(reaction, user):
                return user == ctx.author and \
                       str(reaction.emoji) == '➡️' and \
                       reaction.message.id == message.id

            await asyncio.sleep(3)

            try:
                await self.bot.wait_for("reaction_add", check=check,
                                        timeout=120)
            except asyncio.TimeoutError:
                return

        await message.delete()

        message = await ctx.send(address="classes")

        class_emojis = ['👹', '🧙', '🗡️', '🛡️', '🏹']
        for emoji in class_emojis:
            await message.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.author and \
                   reaction.message.id == message.id and \
                   str(reaction.emoji) in class_emojis

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", check=check,
                                                  timeout=120)
        except asyncio.TimeoutError:
            return

        emoji = str(reaction.emoji)


def setup(bot):
    cog = Duel(bot)
    bot.add_cog(cog)
