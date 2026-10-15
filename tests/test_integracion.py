"""I1: archivo real + motor + consola funcionando juntos hasta un final."""
import pytest

import jugar
from motor import Sesion, cargar_historia
from tests.conftest import RUTA_FARO, RUTA_TRANSMISION


@pytest.mark.parametrize(
    "camino, final, variables",
    [
        (["revisar", "investigar", "activar_codigo"], "E4", {"conoce_origen": True, "confia_en_la_voz": True}),
        (["revisar", "continuar", "activar_sin_verificar"], "E5", {"conoce_origen": False, "confia_en_la_voz": True}),
        (["revisar", "investigar", "cortar"], "E6", {"conoce_origen": True, "confia_en_la_voz": False}),
    ],
    ids=["E4_rescate", "E5_eco", "E6_silencio"],
)
def test_I1_archivo_real_hasta_cada_final(camino, final, variables):
    s = Sesion(cargar_historia(RUTA_TRANSMISION))
    for op in camino:
        assert s.elegir(op).aceptada
    assert s.escena_actual.id == final and s.terminada
    assert s.variables == variables


@pytest.mark.parametrize(
    "camino, final, vars_en_E3",
    [
        (["revisar", "investigar", "activar_codigo"], "E4", {"conoce_origen": True, "confia_en_la_voz": False}),
        (["revisar", "continuar", "activar_sin_verificar"], "E5", {"conoce_origen": False, "confia_en_la_voz": False}),
        (["revisar", "investigar", "cortar"], "E6", {"conoce_origen": True, "confia_en_la_voz": False}),
    ],
    ids=["deshacer_desde_E4", "deshacer_desde_E5", "deshacer_desde_E6"],
)
def test_I1_deshacer_desde_un_final_con_archivo_real(camino, final, vars_en_E3):
    s = Sesion(cargar_historia(RUTA_TRANSMISION))
    for op in camino:
        s.elegir(op)
    assert s.escena_actual.id == final and s.terminada
    assert s.deshacer().aceptada
    assert s.escena_actual.id == "E3" and not s.terminada
    assert s.variables == vars_en_E3
    assert not s.deshacer().aceptada and s.escena_actual.id == "E3"


def test_I1_consola_deshacer_desde_final(capsys):
    # E2 -> investigar -> E3 -> cortar -> E6, deshacer en el final, volver a E3 y elegir otra cosa
    entradas = iter(["1", "1", "2", "d", "1", "n"])
    jugar.jugar(Sesion(cargar_historia(RUTA_TRANSMISION)), entrada=lambda _: next(entradas))
    salida = capsys.readouterr().out
    assert "[E6]" in salida and "Se deshizo la última decisión." in salida and "[E4]" in salida


def test_I1_consola_de_extremo_a_extremo(capsys):
    # entradas inválidas intercaladas + reinicio + segunda partida
    entradas = iter(["x", "9", "1", "1", "2", "s", "1", "2", "1", "n"])
    jugar.jugar(Sesion(cargar_historia(RUTA_TRANSMISION)), entrada=lambda _: next(entradas))
    salida = capsys.readouterr().out
    assert "Entrada no válida" in salida
    assert "[E6]" in salida and "[E5]" in salida
    assert salida.count("FIN DE LA HISTORIA") == 2


@pytest.mark.parametrize("camino, final", [(["revisar", "abrir"], "F3"), (["subir", "esperar"], "F4")])
def test_segunda_historia_con_el_mismo_motor(camino, final):
    s = Sesion(cargar_historia(RUTA_FARO))
    for op in camino:
        assert s.elegir(op).aceptada
    assert s.escena_actual.id == final and s.terminada


def test_segunda_historia_condicion_oculta_opcion():
    s = Sesion(cargar_historia(RUTA_FARO))
    s.elegir("subir")
    assert [o.id for o in s.opciones_disponibles()] == ["esperar"]
    assert not s.elegir("abrir").aceptada
