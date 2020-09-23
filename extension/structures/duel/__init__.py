from .duel import Environment, MortalPlayer


class _class_type:
    def __init__(self, name, emoji):
        self.name = name
        self.emoji = emoji

    def __str__(self):
        return self.name


class CLASSES:
    DEMON = _class_type("Demon", '👹')
    MAGE = _class_type("Mage", '🧙')
    WARRIOR = _class_type("Warrior", '🛡️')
    ASSASSIN = _class_type("Assassin", '🗡️')
    SHOOTER = _class_type("Shooter", '🏹')

    ALL = [DEMON, MAGE, WARRIOR, ASSASSIN, SHOOTER]

    EMOJIS = [class_.emoji for class_ in ALL]
