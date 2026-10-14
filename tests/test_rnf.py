"""Verificación automatizada de los tres requisitos no funcionales."""
import hashlib
import random
from pathlib import Path

import pytest

import jugar
from motor import ErrorContenido, Sesion, cargar_historia, construir_historia
from tests.conftest import RAIZ, RUTA_FARO, RUTA_TRANSMISION
from tests.test_validacion import CASOS


def _huella_motor() -> str:
    h = hashlib.sha256()
    for f in sorted((RAIZ / "motor").glob("*.py")):
        h.update(f.read_bytes())
    return h.hexdigest()


def test_RNF01_modificabilidad_nueva_historia_sin_tocar_motor():
    """RNF01: cargar y terminar una historia nueva modifica 0 archivos de motor/."""
    antes = _huella_motor()
    s = Sesion(cargar_historia(RUTA_FARO))
    s.elegir("revisar"); s.elegir("abrir")
    assert s.terminada
    assert _huella_motor() == antes
    # además: el código del motor no contiene IDs de la historia de referencia
    codigo = "".join(f.read_text(encoding="utf-8") for f in (RAIZ / "motor").glob("*.py"))
    for id_escena in ("\"E1\"", "\"E2\"", "\"E3\"", "'E1'", "'E3'", "conoce_origen"):
        assert id_escena not in codigo


@pytest.mark.parametrize("mutar, codigo, ubicacion", [c[1:] for c in CASOS], ids=[c[0] for c in CASOS])
def test_RNF02_claridad_cada_error_tiene_codigo_causa_y_ubicacion(datos_validos, mutar, codigo, ubicacion):
    """RNF02: 100 % de los errores incluyen categoría, causa no vacía y campo/ID; sin trazas."""
    mutar(datos_validos)
    with pytest.raises(ErrorContenido) as exc:
        construir_historia(datos_validos)
    for e in exc.value.errores:
        assert e.codigo and e.mensaje and e.ubicacion
    assert "Traceback" not in str(exc.value)


def test_RNF03_confiabilidad_1000_entradas_aleatorias_sin_cierre_inesperado(capsys):
    """RNF03: 0 excepciones no controladas ante 1000 entradas aleatorias en consola."""
    rng = random.Random(2026)
    alfabeto = ["", " ", "0", "1", "2", "3", "-1", "99", "abc", "1.5", "s", "ñ", "🙂", "\t"]
    it = iter([rng.choice(alfabeto) for _ in range(1000)])

    def entrada(_):
        try:
            return next(it)
        except StopIteration:
            raise EOFError  # fin de la entrada estándar: main() lo trata como salida controlada

    try:
        jugar.jugar(Sesion(cargar_historia(RUTA_TRANSMISION)), entrada=entrada)
    except EOFError:
        pass  # única terminación aceptada; cualquier otra excepción hace fallar la prueba


def test_RNF03_estado_intacto_ante_1000_ids_invalidos():
    s = Sesion(cargar_historia(RUTA_TRANSMISION))
    rng = random.Random(7)
    for _ in range(1000):
        antes = (s.escena_actual.id, s.variables)
        intento = rng.choice(["activar_codigo", "x", "", "E2", "cortar ", "REVISAR"])
        if not s.elegir(intento).aceptada:
            assert (s.escena_actual.id, s.variables) == antes
