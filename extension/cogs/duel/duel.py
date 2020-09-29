import discord
from discord.ext import commands
from PIL import Image, ImageFont, ImageDraw

import asyncio
import traceback
import io

from extension import structures
from extension.structures import utils
from extension.structures.duel import classes


class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.perfil_background = Image.open("extension/assets/images/perfil_bg.png")

        self.perfil_font = ImageFont.truetype("extension/assets/fonts/Pastika.ttf", size=30)

        self.duels = []

        self.queue = list()
        self.queue_task = bot.loop.create_task(self.queue_selector())

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
                except discord.errors.Forbidden:
                    pass

                try:
                    address = base_address + player_two.language
                    await self.bot.send(player_two, address)
                except discord.errors.Forbidden:
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
        except discord.errors.Forbidden:
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
        if ctx.player:
            return await ctx.send("already-duelist")

        messages = utils.get_address_result("Others.change-language-message")
        message = await ctx.channel.send('\n'.join(messages))

        #await asyncio.sleep(10)

        notes = utils.get_address_result("Commands.start.note")
        for text in utils.get_address_result("Commands.start.phrases"):
            break

            text = text[ctx.server.language]
            text += "\n\n" + notes[ctx.server.language]

            try:
                await message.edit(content=text)
            except discord.errors.NotFound:
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
                return await message.delete()

        await message.delete()

        classes_ = [f"{class_!s} ({class_.emoji})" for class_ in classes.ALL]
        classes_ = utils.join_values(*classes_, separator=ctx.or_separator)

        message = await ctx.send(address="classes", classes=classes_)

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
            return await message.delete()

        emoji = str(reaction.emoji)
        class_ = classes.get_by_emoji(emoji)

        message = await ctx.send(address="confirm", class_=class_)
        
        def check(message):
            return message.channel == ctx.channel and \
                   message.author == ctx.author and \
                   message.content.lower() in ["confirm", "cancel"]

        try:
            response = await self.bot.wait_for("message", check=check,
                                               timeout=120)
        except asyncio.TimeoutError:
            return
        finally:
            await message.delete()

        result = response.content.lower()
        if result == "cancel":
            return

        try:
            await self.bot.new_duelist(ctx.author.id, class_)
        except ValueError:
            # Pode acontecer do comando ser executado duas vezes por uma
            # pessoa, se um comando for completado, o outro acabará
            # gerando esse erro.
            await ctx.send(address="already-duelist")
        else:
            await ctx.send(address="result")

    @structures.bot.is_duelist()
    @commands.command(name="perfil")
    async def perfil_command(self, ctx, player: discord.User=None):
        if not player:
            player = ctx.author

        message = await ctx.send(address="loading")

        player_avatar_bytes = await utils.get_request_bytes(
            self.bot.session, str(player.avatar_url))

        with io.BytesIO(player_avatar_bytes) as fp:
            player_avatar = Image.open(fp)

        player_tag = str(player)

        player = await self.bot.get_player(player.id)

        image = self.perfil_background.copy()

        # Posiciona a imagem do usuário
        player_avatar = player_avatar.resize((98, 96))
        image.paste(player_avatar, (420, 79), player_avatar.convert("RGBA"))

        # Posiciona a tag do usuário
        # O Y da reta é 114
        # Ponto esquerdo (pE) da reta se encontra no X = 90
        # Ponto direito da (pD) reta se encontra no X = 390
        # O meio entre os dois pontos é 240, a expressão usada
        # foi: `(pD - pE) / 2 + pE` -> (390 - 90) / 2 + 90 = 240

        # Para posicionar algo no meio da reta, é necessário pegar o comprimento da coisa a ser posicionada e dividir por dois, depois disso subtrair o valor que deu no valor do meio da reta e utilizar a posição que resultou.
        # Expressão (lineWidth - width / 2)

        font = self.perfil_font

        draw = ImageDraw.Draw(image)
        w, h = draw.textsize(player_tag, font=font)
        draw.text((240 - w // 2, 114 - h - 3),
                  player_tag, fill=(0, 0, 0),
                  font=font)

        # class_image = Image.open("mage.png")
        # class_image = class_image.resize((144 - 16, 135 - 16))

        # bg.paste(class_image, (377 + 8, 230 + 8), class_image.convert("RGBA"))

        # class_name = "Mage"
        # w, h = draw.textsize(class_name, font=font)
        # x = 377 + w // 2
        # y = 135 + ((230 + 135) / 2) - (135 // 58)
        # draw.text((x, y), class_name, fill=(255, 255, 255), font=font)

        badges_word = "Badges"
        w, _ = draw.textsize(badges_word, font=font)
        draw.text((95, 270), badges_word, fill=(0, 0, 0), font=font)

        draw.line(((95 + w + 3, 278), (356, 278)), (0, 0, 0), 7)

        w, _ = draw.textsize(str(player.coins), font=font)
        draw.text(((120 + (300 - 120) / 2) - (w / 2), 235),
                  str(player.coins), fill=(0, 0, 0), font=font)

        victory_word = "Victories:"
        w, _ = draw.textsize(victory_word, font=font)
        draw.text((112, 132), victory_word, fill=(0, 255, 75), font=font)

        draw.text((112 + w + 5, 132), str(player.wins), fill=(0,0,0), font=font)

        defeat_word = "Defeats:"
        w, _ = draw.textsize(defeat_word, font=font)
        draw.text((112, 187), defeat_word, fill=(255, 0, 75), font=font)

        draw.text((112 + w + 5, 187), str(player.losts), fill=(0,0,0), font=font)

        with io.BytesIO() as fp:
            image.save(fp, format="png")
            fp.seek(0)

            player_image = discord.File(fp, filename=f"{ctx.author}-image.png")
        await ctx.rsend(file=player_image)


def setup(bot):
    cog = Duel(bot)
    bot.add_cog(cog)
