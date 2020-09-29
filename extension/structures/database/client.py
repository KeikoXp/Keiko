from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo import errors as db_errors
from collections import defaultdict

from . import models
from extension.structures import utils


class DatabaseClient:
    def __init__(self, url: str):
        connection = AsyncIOMotorClient(url)

        database = connection["Marjorie"]

        self.servers: AsyncIOMotorCollection = database["Servers"]
        self.players: AsyncIOMotorCollection = database["Players"]

        self._cache = defaultdict(utils.Cache)

    def _raw_data_to_model(self, collection, data):
        """
        Parametros
        ----------
        collection : AsyncIOMotorCollection
        data : dict

        Retorno
        -------
        models.DatabaseModel
        """
        if collection == self.servers:
            return models.Server(data)
        elif collection == self.players:
            return models.Player(data)

        raise NameError("invalid collection")

    async def _insert_into_cache(self, collection, data):
        if type(data) is dict:
            data = self._raw_data_to_model(collection, data)

        cache_collection = self._cache[collection.name]

        data_droped = cache_collection.add(id, data)
        if data_droped:
            await self._update_data(collection, data_droped)


    async def _update_data(self, collection, data):
        """
        Parametros
        ----------
        collection : AsyncIOMotorCollection
        data : typing.Union[models.DatabaseModel, dict]
        """
        if issubclass(data.__class__, models.DatabaseModel):
            data = data.to_dict()
        elif type(data) is dict:
            pass
        else:
            raise TypeError("dict or models.DatabaseModel expected")

        filter = {"_id": data["_id"]}
        await collection.update_one(filter, data)

        # NOTE
        # Não faça com que essa função coloque os dados em cache, os
        # dados vieram de lá provavelmente e a única coisa que precisa
        # ser atualizada é o banco de dados.

    async def _get_data(self, collection, id):
        """
        Pode retornar `None`.

        Parametros
        ----------
        collection : AsyncIOMotorCollection
        id : typing.Any

        Retorno
        -------
        models.DatabaseModel
        """
        cache_collection = self._cache[collection.name]

        try:
            return cache_collection[id]
        except KeyError:
            data = await collection.find_one({"_id": id})

            if not data:
                return

            data = self._raw_data_to_model(collection, data)

            await self._insert_into_cache(collection, data)

            return data

    async def _new_data(self, collection, data):
        """
        Parametros
        ----------
        collection : AsyncIOMotorCollection
        data : typing.Union[models.DatabaseModel, dict]
        """
        try:
            if issubclass(data.__class__, models.DatabaseModel):
                data = data.to_dict()

            await collection.insert_one(data)
        except:
            raise
        else:
            await self._insert_into_cache(collection, data)

    async def get_server(self, id: int) -> models.Server:
        """
        Retorna as informações do servidor, retorna `None` se não
        encontrado.

        Parametros
        ----------
        id : int
            Discord ID do servidor.

        Retorno
        -------
        models.Server
        """
        if type(id) is not int:
            raise TypeError("int expected in `id` parameter")

        return await self._get_data(self.servers, str(id))

    async def get_player(self, id: int) -> models.Player:
        """
        Retorna as informações do jogador, retorna `None` se não
        encontrado.

        Parametros
        ----------
        id : int
            Discord ID do jogador.

        Retorno
        -------
        models.Player
        """
        if type(id) is not int:
            raise TypeError("int expected in `id` parameter")

        return await self._get_data(self.players, str(id))

    async def new_server(self, server: models.Server) -> None:
        """
        Parametros
        ----------
        server : models.Server

        Raises
        ------
        ValueError
            O servidor já foi registrado.
        """
        if type(server) is not models.Server:
            raise TypeError("models.Server expected in `server` parameter")

        try:
            await self._new_data(self.servers, server)
        except db_errors.DuplicateKeyError:
            raise ValueError("guild already registred")

    async def new_player(self, player: models.Player) -> None:
        """
        Parametros
        ----------
        player : models.Player

        Raises
        ------
        ValueError
            O jogador já foi registrado.
        """
        if not isinstance(player, models.Player):
            raise TypeError("models.Player expected in `player` parameter")

        try:
            await self._new_data(self.players, player)
        except db_errors.DuplicateKeyError:
            raise ValueError("player already registred")
