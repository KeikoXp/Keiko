from enum import Enum
import typing

from .abstract import Action


class Classes(Enum):
    ASSASSIN = "Assassino"
    WARRIOR  = "Guerreiro"

def action(emoji) -> Action:
    """
    Parameters
    ----------
    emoji : 
    """
    def decorator(function):
        return Action(function, emoji)
    return decorator


class MortalPlayer:
    def __init__(self, player, user):
        self.user = user

        self._life = int()

        self.class_ = player.class_

        if self.class_ == Classes.ASSASSIN:
            self.evasion_stack = 0
            self.max_evasion_stack = 3

    @property
    def life(self) -> int:
        """Returns the life of player."""
        return self._life

    @property
    def dead(self) -> bool:
        return self._life < 1

    @property
    def invisible(self) -> bool:
        try:
            return self.evasion_stack == self.max_evasion_stacks
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
        pass

    @hide.check
    def hide(self) -> bool:
        return not self.invisible


class Environment:
    def __init__(self, players, bot):
        self.players = players
        self.bot = bot

    async def start(self):
        """
        Inicia o ambiente do duelo.
        """
        pass
