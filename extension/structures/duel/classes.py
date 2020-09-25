import difflib

from .abstract import Explainable


class Class(Explainable):
    def __init__(self, emoji, **options):
        self.emoji = emoji

        self.name = self.__class__.__name__
        self.description = self.__doc__

        self.show_life = options.pop("show_life", True)
        self.show_mana = options.pop("show_mana", False)
        self.show_stamina = options.pop("show_stamina", False)

    def __explication__(self):
        return self.description

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if type(other) is not self:
            return False

        return other.name == self.name

    def __nq__(self, other):
        return not self == other

    def is_demon(self) -> bool:
        """Diz se a classe é a classe de Demônio."""
        return self.name == "Demon"

    def is_mage(self) -> bool:
        """Diz se a classe é a classe de Mago."""
        return self.name == "Mage"

    def is_warrior(self) -> bool:
        """Diz se a classe é de Guerreiro."""
        return self.name == "Warrior"

    def is_assassin(self) -> bool:
        """Diz se a classe é de Assassino."""
        return self.name == "Assassin"

    def is_shooter(self) -> bool:
        """Diz se a classe é de Atirador."""
        return self.name == "Shooter"


class Demon(Class):
    """
    **Demônio**

    Fal algo :D
    """
    def __init__(self):
        super().__init__('👹', show_stamina=True)


class Mage(Class):
    """
    **Mago**

    Fal algo :D
    """
    def __init__(self):
        super().__init__('🧙', show_mana=True)


class Warrior(Class):
    """
    **Guerreiro**

    Fal algo :D
    """
    def __init__(self):
        super().__init__('🛡️', show_stamina=True)
        
        
class Assassin(Class):
    """
    **Assassino**

    Fal algo :D
    """
    def __init__(self):
        super().__init__('🗡️', show_stamina=True) 


class Shooter(Class):
    """
    **Atirador**

    Fal algo :D
    """
    def __init__(self):
        super().__init__('🏹', show_stamina=True)


ALL = [class_() for class_ in Class.__subclasses__()]
EMOJIS = [class_.emoji for class_ in ALL]

def get_by_name(name: str, *, get_matches: bool=False):
    """
    Retorna uma classe pelo nome ou classes com nome parecidos.
    Retorna `None` ou uma lista vazia se não for encontrado.

    Parametros
    ----------
    name : str
        Nome da classe.

    get_matches : bool (False)
        Retorna as classes com nome parecido ao informado.

    Retorno
    -------
    Se `get_matches` for `False`, retorna um objeto do `Class`, caso
    contrário, retorna uma lista com items do tipo `Class`.
    """
    if type(name) is not str:
        raise TypeError("str expected")

    if get_matches:
        return difflib.get_close_matches(name, ALL)

    for class_ in ALL:
        if class_.name == name:
            return class_

def get_by_emoji(emoji) -> Class:
    """
    Retorna uma classe pelo emoji dela.
    Retorna `None` se não for encontrado.

    Parametros
    ----------
    emoji : typing.Union[str, discord.Emoji, discord.PartialEmoji]
        Emoji da classe.

    Retorno
    -------
    Class
        A classe.
    """
    for class_ in ALL:
        if class_.emoji == emoji:
            return class_
