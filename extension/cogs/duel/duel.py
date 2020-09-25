from discord.ext import commands
from discord import errors as discord_errors

import asyncio
import traceback

from extension import structures
from extension.structures import utils
from extension.structures.duel import classes


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

            player_one = structures.duel.MortalPlayer(player_one_data,
                                                      player_one)
            player_two = structures.duel.MortalPlayer(player_two_data,
                                                      player_two)
            # Cria as estruturas para que os duelistas possam duelar.

            players = (player_one, player_two)

            env = structures.duel.Environment(players, self.bot)
            self.bot.envs.append(env)
            # Guardar o ambiente em que o duelo está acontencendo é
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
                    self.queue.pop(index)
                    # Retira o `player_two` da queue.

                    coroutine = self.match(player_one, player_two)
                    self.bot.create_task(coroutine)
                    # É extramemente necessário criar uma task, além de não
                    # interromper a execução do código, fará com que erros
                    # gerados na função também não interrompão o código.

                    break

            await asyncio.sleep(1)

    @structures.bot.is_duelist()
    @structures.bot.not_dueling()
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
        message = await ctx.channel.send('\n'.join(messages))

        await asyncio.sleep(10)

        notes = utils.get_address_result("Commands.start.note")
        for text in utils.get_address_result("Commands.start.phrases"):
            text = text[ctx.server.language]
            text += "\n\n" + notes[ctx.server.language]

            try:
                await message.edit(content=text)
            except discord_errors.NotFound:
                message = await ctx.channel.send(text)
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

        classes = [f"{class_.name} ({class_.emoji})" for class_ in classes.ALL]
        classes = utils.join_list(classes, separator=ctx.or_separator)
        message = await ctx.send(address="classes", classes=classes)

        for emoji in classes.EMOJIS:
            await message.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.author and \
                   reaction.message.id == message.id and \
                   str(reaction.emoji) in classes.EMOJIS

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", check=check,
                                                  timeout=120)
        except asyncio.TimeoutError:
            return

        emoji = str(reaction.emoji)
        class_ = classes.get_by_emoji(emoji)

        message = await ctx.send(address="confirm", class_=class_)
        
        def check(message):
            return message.channel == ctx.channel and \
                   message.author == ctx.author and \
                   message.content.lower() in ["confirm", "cancel"]

        try:
            message = await self.bot.wait_for("message", check=check,
                                              timeout=120)
        except asyncio.TimeoutError:
            return
        finally:
            await message.delete()

        result = message.content.lower()
        if result == "cancel":
            return





def setup(bot):
    cog = Duel(bot)
    bot.add_cog(cog)
