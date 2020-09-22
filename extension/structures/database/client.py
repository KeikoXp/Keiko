from motor.motor_asyncio import AsyncIOMotorClient

from . import models


class DatabaseClient:
    def __init__(self, url: str):
        connection = AsyncIOMotorClient(url)

        database = connection["Marjorie"]

        self.servers = database["Servers"]
        self.players = database["Players"]

    async def get_server(self, id: int) -> models.Server:
        """
        Returns the data of server, can return `None`.

        Parameters
        ----------
        id : int

        Returns
        -------
        models.Server
        """
        if type(id) is not int:
            raise TypeError("int expected in `id` parameter")

        return await self.servers.find_one({"_id": str(id)})

    async def get_player(self, id: int):
        """
        Returns the data of player, can return `None`.

        Parameters
        ----------
        id : int

        Returns
        -------
        models.Player
        """
        if type(id) is not int:
            raise TypeError("int expected in `id` parameter")

        return await self.players.find_one({"_id": str(id)})

    async def new_server(self, server: models.Server):
        """
        Parameters
        ----------
        server : models.Server
        """
        if not isinstance(server, models.Server):
            raise TypeError("models.Server expected in `server` parameter")

        server = server.to_dict()
        try:
            return await self.servers.insert_one(server)
        # except db_errors.DuplicateKeyError:
        except BaseException as e:
            raise e

    async def new_player(self, player: models.Player):
        if not isinstance(player, models.Player):
            raise TypeError("models.Player expected in `player` parameter")

        player = player.to_dict()
        try:
            return await self.players.insert_one(player)
        # except db_errors.DuplicateKeyError:
        except BaseException as e:
            raise e
