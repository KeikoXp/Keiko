import json
import inspect

with open("translations.json", encoding="utf-8") as file:
    translations = json.load(file)


def join_address(*values):
    """
    Junta os valores para formar um endereço.
    """
    values = list(values)
    for index, value in values:
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
