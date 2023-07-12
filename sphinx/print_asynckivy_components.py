import typing as T
from importlib import import_module
from importlib.resources.abc import Traversable
from importlib.resources import Package, files
from sphinx.ext.autodoc.mock import mock


def enum_private_submodules(package: Package) -> T.Iterator[Traversable]:
    for c in files(package).iterdir():
        name = c.name
        if name.endswith(".py") and name.startswith("_") and (not name.startswith("__")):
            yield c


def enum_components(module_name: str) -> T.Iterator[str]:
    return iter(import_module(module_name).__all__)


def enum_asynckivy_components() -> T.Iterator[str]:
    with mock(["kivy", ]):
        for submod in enum_private_submodules("asynckivy"):
            fullname = "asynckivy." + submod.name[:-3]
            yield from enum_components(fullname)


def main():
    names = sorted(enum_asynckivy_components())
    print(''.join((
        "__all__ = (\n    '",
        "',\n    '".join(names),
        "',\n)\n",
    )))



if __name__ == "__main__":
    main()
