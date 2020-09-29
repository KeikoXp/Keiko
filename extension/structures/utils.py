import aiohttp

import json
import inspect
import collections

with open("translations.json", encoding="utf-8") as file:
    translations = json.load(file)


def join_address(*values):
    """
    Junta os valores para formar um endereço.
    """
    values = list(values)
    for index, value in enumerate(values):
        values[index] = value.strip('.')
    return '.'.join(values)


def get_address_result(addres: str, placeholders: dict = {}):
    result = translations
    for key in addres.split('.'):
        result = result[key]

    if placeholders:
        if type(result) is str:
            result = result.format(**placeholders)
        else:
            for index, value in enumerate(result):
                result[index] = value.format(**placeholders)

    return result


def experience_to_level_up(level: int) -> int:
    """
    Parametros
    ----------
    level : int

    Retorno
    -------
    int
        Quantidade de experiência para o próximo nível.
    """
    return int(level * 50 + (level * 50 / 2))


def join_values(*values, separator: str) -> str:
    """
    Junta valores entre vírgulas e insere `separator` no final.

    Exemplos
    --------
    >>> join_values(1, 2, 3, separator='e')
    '1, 2 e 3'
    >>> join_values('Nium', 'Marjorie', separator='e')
    'Nium e Marjorie'
    >>> join_values('Sim', 'Não', seprator='ou')
    'Sim ou Não'

    Parametros
    ----------
    *values : typing.Tuple[typing.Any]
        Os valores que serão juntados.
    separator : str
        O último separador que será colocado.

    Retorno
    -------
    str
        O resultado da junção.
    """
    left, right = values[:-1], values[-1]
    left, right = ", ".join(map(str, left)), str(right)

    # `values` pode ser entendido como typing.Tuple[typing.Any],
    # `str.join` precisa de um iterador que retorne objetos do tipo
    # `str` então, para aceitar números ou qualquer outra coisa, é
    # necessário pegar a representação em string desses objetos.

    if left and right:
        separator = f" {separator} "
    else:
        return right

    return separator.join([left, right])

def check_type_hints(function):
    """
    Verifica todos os type hints da função, até o retorno.
    """
    signature = inspect.signature(function)
    parameters = signature.parameters

    def wrapper(*args, **kwargs):
        signature_result = signature.bind(*args, **kwargs)
        signature_result.apply_defaults()

        for parameter, argument in signature_result.arguments.items():
            parameter = parameters[parameter]
            type_hint = parameter.annotation

            if type_hint != inspect._empty:
                if type(argument) != type_hint:
                    error = "{0!r} expected in {1!r} parameter".format(
                        type_hint.__name__, parameter.name)
                    raise TypeError(error)

        result = function(*args, **kwargs)

        if signature.return_annotation:
            if type(result) != signature.return_annotation:
                raise TypeError(
                    "{0!r} returned in {1!r} function, {2!r} expected".format(
                        type(result).__name__, function.__name__,
                        signature.return_annotation.__name__)
                    )

        return result
    return wrapper


async def get_request_bytes(session: aiohttp.ClientSession, url: str) -> bytes:
    async with session.get(url) as response:
        return await response.read()


class Stack:
    """
    Atributos
    ---------
    value : int
        Valor do stack.
    max : int
        Valor máximo que `value` pode chegar.
    """
    __slots__ = ("value", "max")

    def __init__(self, max: int):
        self.value = 0
        self.max = max

    @property
    def full(self) -> bool:
        """Diz se o stack está no máximo."""
        return self.value >= self.max

    def increase(self) -> None:
        """Incrementa o stack em um se possível."""
        if self.value + 1 <= self.max:
        # if not self.full:
            self.value += 1

    def reset(self) -> None:
        """Reseta o valor do stack."""
        self.value = 0


class Cache(collections.OrderedDict):
    def __init__(self, limit: int=100):
        super().__init__()

        self.limit = limit

    def __setitem__(self, *args):
        item_poped = None
        if len(self) == self.limit:
            item_poped = self.popitem(last=False)

        super().__setitem__(*args)
        return item_poped

    def add(self, name, value):
        return self.__setitem__(name, value)
