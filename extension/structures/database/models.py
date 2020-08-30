import discord
import typing


class Player:
    def __init__(self, raw_data: dict):
        if type(raw_data) is not dict:
            raise TypeError("dict expected in 'raw_data' parameter")
 
        self._db_id = raw_data.get("_id", None)
        if not self._db_id:
            raise RuntimeError("'_id' not defined in 'raw_data'")
 
        self._dbclass = raw_data.pop("class", None)

        self._dbexperience = raw_data.pop("experience", int())
        self._dblevel = raw_data.pop("level", int())

        self._dbcoins = raw_data.pop("coins", int())
        self._dbgems = raw_data.pop("gems", int())

        self._dbpotions = raw_data.pop("potions", dict())
        self._dbamulets = raw_data.pop("amulets", dict())

    @property
    def class_(self) -> str:
        return self._dbclass

    @property
    def experience(self) -> int:
        return self._dbexperience

    @property
    def level(self) -> int:
        return self._dblevel

    @property
    def coins(self) -> int:
        return self._dbcoins

    @property
    def gems(self) -> int:
        return self._dbgems

    def to_dict(self):
        result = {}

        for key, value in self.__dict__.items():
            if key.startswith("_db") and bool(value):
                key = key[3:]
                result[key] = value

        return result

    def is_duelist(self) -> bool:
        return self.class_ != None


class Server:
    def __init__(self, raw_data: dict):
        if type(raw_data) is not dict:
            raise TypeError("dict expected in 'raw_data' parameter")
 
        self._db_id = raw_data.get("_id", None)
        if not self._db_id:
            raise RuntimeError("'_id' not defined in 'raw_data'")

        self._dbcommand_channels = raw_data.get("command_channels", [])

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
