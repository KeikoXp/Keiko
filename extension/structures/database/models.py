import typing
import datetime

from extension.structures.duel import classes


class Player:
    def __init__(self, raw_data: dict):
        if type(raw_data) is not dict:
            raise TypeError("dict expected in 'raw_data' parameter")

        self.__dict__["_locked"] = True

        self._db_id = raw_data.get("_id", None)
        if not self._db_id:
            raise RuntimeError("'_id' not defined in 'raw_data'")

        self._dbclass = raw_data.pop("class", None)

        self._dbexperience = raw_data.pop("experience", int())
        self._dblevel = raw_data.pop("level", int())

        self._dbcoins = raw_data.pop("coins", int())

        self._dbpotions = raw_data.pop("potions", dict())
        self._dbamulets = raw_data.pop("amulets", dict())

        self._dbvotes = raw_data.pop("votes", int())
        self._dbdaily_cooldown = raw_data.pop("daily_cooldown", None)

        self.need_update = False
        self.__dict__["_locked"] = False

    @property
    def class_(self) -> typing.Union[classes.Class, None]:
        """
        Retorna a classe do jogador. Pode ser `None`.
        """
        return classes.get_by_name(self._dbclass)

    @property
    def experience(self) -> int:
        """
        Retorna a quantidade de experiência do usuário.
        """
        return self._dbexperience

    @property
    def level(self) -> int:
        """
        Retorna o nível do usuário.
        """
        return self._dblevel

    @property
    def coins(self) -> int:
        """
        Retorna as modeas do usuário.
        """
        return self._dbcoins

    @property
    def votes(self) -> int:
        """
        Retorna a quantidade de votos do usuário.
        """
        return self._dbvotes

    @property
    def daily_reward_in_cooldown(self) -> datetime.datetime:
        if datetime.datetime.now() > self._dbdaily_cooldown:
            return self._dbdaily_cooldown

        self._dbdaily_cooldown = None

    def to_dict(self) -> dict:
        result = {}

        for key, value in self.__dict__.items():
            if key.startswith("_db") and bool(value):
                key = key[3:]
                result[key] = value

        return result

    def is_duelist(self) -> bool:
        return bool(self.class_)

    def __setattr__(self, name: str, value: typing.Any):
        if not self._locked and name.startswith("_db"):
            self.__dict__["need_update"] = True

        self.__dict__[name] = value


class Server:
    def __init__(self, raw_data: dict):
        if type(raw_data) is not dict:
            raise TypeError("dict expected in 'raw_data' parameter")

        self._db_id = raw_data.get("_id", None)
        if not self._db_id:
            raise RuntimeError("'_id' not defined in 'raw_data'")

        self._dblanguage = raw_data.pop("language", "english")

        self._dbcommand_channels = raw_data.get("command_channels", [])

    @property
    def language(self) -> str:
        return self._dblanguage

    @property
    def command_channels(self) -> typing.List[str]:
        return self._dbcommand_channels

    def to_dict(self) -> dict:
        result = {}

        for key, value in self.__dict__.items():
            if key.startswith("_db") and bool(value):
                key = key[3:]
                result[key] = value

        return result

    def is_command_channel(self, channel_id: id) -> bool:
        """
        Parameters
        ----------
        channel_id : int
            Discord ID of the TextChannel.

        Returns
        -------
        bool
        """
        if not self._dbcommand_channels:
            return True

        if type(channel_id) is int:
            raise TypeError("int expected in `channel_id` parameter")

        return str(channel_id) in self._dbcommand_channels

    @classmethod
    def new(cls, id: int):
        return cls({"_id": id})
