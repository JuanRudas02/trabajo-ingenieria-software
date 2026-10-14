import copy
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
HISTORIAS = RAIZ / "historias"
RUTA_TRANSMISION = HISTORIAS / "la_ultima_transmision.json"
RUTA_FARO = HISTORIAS / "el_faro.json"


@pytest.fixture
def datos_validos():
    """Copia profunda de la historia de referencia, para mutarla en cada prueba."""
    return copy.deepcopy(json.loads(RUTA_TRANSMISION.read_text(encoding="utf-8")))


@pytest.fixture
def sesion():
    from motor import Sesion, cargar_historia
    return Sesion(cargar_historia(RUTA_TRANSMISION))
