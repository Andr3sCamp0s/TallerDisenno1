"""Hace que sus pruebas cuenten dentro de la etapa 5."""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))


def pytest_collection_modifyitems(items):
    for item in items:
        if "mis_pruebas" in str(item.fspath):
            item.add_marker(pytest.mark.etapa5)
