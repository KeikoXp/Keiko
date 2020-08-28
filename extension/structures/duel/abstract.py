import discord

import typing
import abc

Emoji = typing.Union[str, discord.Emoji, discord.PartialEmoji]


class Buyable:
    def __init__(self, name: str, price: typing.Tuple[int, int], emoji: str):
        if type(name) is not str:
            raise TypeError("str expected in `name` parameter")

        if type(price) is not tuple:
            raise TypeError("tuple expected in `price` parameter")

        if not isinstance(emoji, (str, discord.Emoji, discord.PartialEmoji)):
            raise TypeError(f"{Emoji} expected in `emoji` parameter")

        try:
            x, y = price
        except ValueError:
            raise IndexError("`price` need to be two values")

        if type(x) != type(y) != int:
            raise TypeError("the values of `price` need to be integer")

        self.name = name
        self.price = price
        self.emoji = emoji

    def string_price(self) -> str:
        """Return the `price` how a string."""
        strings = []

        coins, gems = self.price
        if coins:
            strings.append(f"{coins} <coin-emoji>")

        if gems:
            strings.append(f"{gems} <gem-emoji>")

        return " | ".join(strings) + '!'


class Explainable(abc.ABC):
    @abc.abstractmethod
    def __explication__(self) -> str:
        raise NotImplementedError()


class Executable(abc.ABC):
    @abc.abstractmethod
    def execute(self, *args, **kwargs) -> typing.Any:
        raise NotImplementedError()


class Skill(Buyable, Explainable, Executable):
    def execute(self, player, enemy) -> typing.Tuple[str, dict]:
        raise NotImplementedError()


class Item(Buyable, Explainable, Executable):
    def execute(self, player, enemy) -> typing.Tuple[str, dict]:
        raise NotImplementedError()


class Action(Executable):
    def __init__(self, target: typing.Callable, emoji: str):
        self.emoji = emoji
        self.__target = target
        self.__check = None

    def is_possible_execute(self) -> bool:
        if not self.__check:
            return False
        return self.__check()

    def check(self, function):
        """-> Decorator"""
        self.__check = function
        return self

    def execute(self, message, player, enemy) -> typing.Tuple[str, dict]:
        """
        Executes the action.

        Parameters
        ----------
        player : duel.MortalPlayer
            The player that will be execute the action.
        enemy : duel.MortalPlayer
            The enemy of player.

        Returns
        -------
        typing.Tuple[str, dict]
        """
        return self.__target(message, player, enemy)

    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)
