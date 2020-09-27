import typing
import datetime

from extension.structures import utils
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
        """Retorna a classe do jogador. Pode ser `None`."""
        return classes.get_by_name(self._dbclass)

    @property
    def experience(self) -> int:
        """Retorna a quantidade de experiência do usuário."""
        return self._dbexperience

    @experience.setter
    def experience(self, new_value):
        # TODO
        # Verificar se vale a pena criar essa verificação abaixo.
        #
        # if type(new_value) is not int:
        #     raise TypeError("you can't change the type")
        
        if new_value < self._dbexperience: # Experiência foi reduzida.
            if new_value <= 0:
                # A experiência não pode ficar negativa.
                new_value = 0
        else: # Experiência foi incrementada ou permanece a mesma.
            experience_to_level_up = utils.experience_to_level_up(self.level)
            
            if new_value >= experience_to_level_up:
                new_value = new_value - experience_to_level_up
                self._dblevel += 1

        self._dbexperience = new_value

    @property
    def level(self) -> int:
        """Retorna o nível do usuário."""
        return self._dblevel

    @level.setter
    def level(self, new_value):
        if new_value < self._dblevel:
            return

        self._dblevel = new_value

    @property
    def coins(self) -> int:
        """Retorna as modeas do usuário."""
        return self._dbcoins

    @coins.setter
    def coins(self, new_value):
        if new_value < self._dbcoins:
            return

        self._dbcoins = new_value

    @property
    def votes(self) -> int:
        """Retorna a quantidade de votos do usuário."""
        return self._dbvotes

    @votes.setter
    def votes(self, new_value):
        if new_value < self._dbvotes:
            return

        self._dbvotes = new_value

    @property
    def daily_reward_in_cooldown(self) -> datetime.datetime:
        """Retorna a data em que o jogador poderá pegar a sua recompensa
        diária."""
        if datetime.datetime.now() > self._dbdaily_cooldown:
            return self._dbdaily_cooldown

        self._dbdaily_cooldown = None

    def to_dict(self) -> dict:
        """Retorna todos os atributos do banco de dados em um dicionário."""
        result = {}

        for key, value in self.__dict__.items():
            if key.startswith("_db") and bool(value):
                key = key[3:]
                result[key] = value

        return result

    def is_duelist(self) -> bool:
        """Diz se o usuário é um duelista,"""
        return bool(self.class_)

    def __setattr__(self, name: str, value: typing.Any):
        if not self._locked and name.startswith("_db"):
            self.__dict__["need_update"] = True

        self.__dict__[name] = value

    @classmethod
    def new_duelist(cls, id: int, class_: classes.Class):
        """
        Cria uma instancia da class baseada no `id` e `class_`.

        Parametros
        ----------
        id : int
            Discord ID do jogador.
        class_ : duel.classes.Class
            Classe do duelista.

        Retorno
        -------
        models.Player
        """
        if type(id) is not int:
            raise TypeError("int expected in `id` parameter")

        if not issubclass(class_.__class__, classes.Class):
            error = "subclass of classes.Class expected in `class_` parameter"
            raise TypeError(error)

        data = {"_id": str(id), "class": str(class_)}
        return cls(data)


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
        """Retorna a língua do servidor."""
        return self._dblanguage

    @property
    def command_channels(self) -> typing.List[int]:
        """
        Retorna todos os IDs dos canais de comandos.

        Retorno
        -------
        typing.List[int]
        """
        return [int(c) for c in self._dbcommand_channels]

    def to_dict(self) -> dict:
        """Retorna todos os atributos do banco de dados em um dicionário."""
        result = {}

        for key, value in self.__dict__.items():
            if key.startswith("_db") and bool(value):
                key = key[3:]
                result[key] = value

        return result

    def is_command_channel(self, channel_id: id) -> bool:
        """
        Diz se o canal é um canal de comandos.

        Parametros
        ----------
        channel_id : int
            Discord ID do canal de texto.

        Retorno
        -------
        bool
        """
        if not self._dbcommand_channels:
            return True

        # Se não houver nenhum canal de comandos definido, todos os
        # outros canais podem ser usados para executar os comandos.

        if type(channel_id) is int:
            raise TypeError("int expected in `channel_id` parameter")

        return str(channel_id) in self._dbcommand_channels

    @classmethod
    def new(cls, id: int):
        """
        Cria uma instancia da classe baseada no `id`.

        Parametros
        ----------
        id : int
            Discord ID do servidor.

        Retorno
        -------
        models.Server
        """
        if type(id) is not int:
            raise TypeError("int expected")

        data = {"_id": str(id)}
        return cls(data)
