import builtins
from typing import Optional

_BUILTINS_DICT = {
    getattr(builtins, name): (getattr(builtins, name), name)
    for name in sorted(dir(builtins))
    if not name.startswith('__')
}


def get_literal_repr(obj: object) -> Optional[str]:
    if type(obj) in (int, float, str, bytes, bytearray, range):
        return repr(obj)

    try:
        b_obj, name = _BUILTINS_DICT[obj]
    except KeyError:
        try:
            return _get_complex_literal_repr(obj)
        except ValueError:
            return None

    if obj is b_obj:
        return name
    return None


def _provide_lit_repr(obj: object) -> str:
    literal_repr = get_literal_repr(obj)
    if literal_repr is None:
        raise ValueError
    return literal_repr


def _parenthesize(parentheses: str, elements) -> str:
    return parentheses[0] + ", ".join(map(_provide_lit_repr, elements)) + parentheses[1]


def _get_complex_literal_repr(obj: object) -> Optional[str]:
    if type(obj) == list:
        return _parenthesize("[]", obj)

    if type(obj) == tuple:
        return _parenthesize("()", obj)

    if type(obj) == set:
        if obj:
            return _parenthesize("{}", obj)
        return "set()"

    if type(obj) == frozenset:
        if obj:
            return "frozenset(" + _parenthesize("{}", obj) + ")"
        return "frozenset()"

    if type(obj) == slice:
        parts = (obj.start, obj.step, obj.stop)  # type: ignore[attr-defined]
        return f"slice" + _parenthesize("()", parts)

    if type(obj) == dict:
        return (
            "{"
            + ", ".join(
                f"{_provide_lit_repr(key)}: {_provide_lit_repr(value)}"
                for key, value in obj.items()  # type: ignore[attr-defined]
            )
            + "}"
        )

    return None
