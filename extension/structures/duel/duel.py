import typing

from .abstract import Action
from extension.structures import utils
from extension.structures.duel import classes


def action(emoji) -> Action:
    """
    Parameters
    ----------
    emoji : typing.Union[str, discord.Emoji, discord.PartialEmoji]
    """
    def decorator(function):
        return Action(function, emoji)
    return decorator


class MortalPlayer:
    def __init__(self, player, user):
        self.user = user

        self._life = int()

        self.class_ = class_ = player.class_

        if class_.is_assassin():
            self.evasion = utils.Stack(3)

    @property
    def life(self) -> int:
        """Retorna a vida do jogador."""
        return self._life

    @property
    def dead(self) -> bool:
        """Diz se o jogador está morto."""
        return self._life < 1

    @property
    def invisible(self) -> bool:
        """Diz se o jogador está invisivel."""
        try:
            return self.evasion.full
        except AttributeError:
            return False

    @action('🗡️')
    async def attack(self, message, player, enemy):
        pass

    @attack.check
    def attack(self) -> bool:
        if not self.invisible:
            return False

        return True

    @action('💖')
    async def rest(self, message, player, enemy):
        pass

    @rest.check
    def rest(self) -> bool:
        return True

    @action('💨')
    async def hide(self, message, player, enemy):
        self.evasion.increase()

    @hide.check
    def hide(self) -> bool:
        return not self.invisible


class Environment:
    def __init__(self, players, bot):
        self.players = players
        self.bot = bot

    async def make_turn(self, player, enemy) -> typing.Tuple[str, str]:
        """
        Faz o turno de um jogador.
        
        Retorno
        -------
        typing.Tuple[str, str]
            Resultado do turno para o jogador e para o seu inimigo.
        """
        messages = ['None', 'None']
        return messages

    async def start(self):
        """
        Inicia o ambiente do duelo.
        """
        player, enemy = self.players
        while all(not player.dead for player in self.players):
            player, enemy = enemy, player

            messages = await self.make_turn(player, enemy)
            message_to_player, message_to_enemy = messages
