"""Pruebas unitarias de reglas: U1, U2, U3, U5 y criterios CA01, CA02."""
import pytest

from motor import Sesion, construir_historia


def ids(opciones):
    return [o.id for o in opciones]


# ---------------- U1: condiciones habilitan solo las opciones correspondientes
@pytest.mark.parametrize(
    "camino, esperadas",
    [
        (["revisar", "investigar"], ["activar_codigo", "cortar"]),          # conoce_origen = true
        (["revisar", "continuar"], ["activar_sin_verificar", "cortar"]),    # conoce_origen = false
    ],
    ids=["conoce_origen_verdadero", "conoce_origen_falso"],
)
def test_U1_condiciones_habilitan_opciones(sesion, camino, esperadas):
    for op in camino:
        assert sesion.elegir(op).aceptada
    assert sesion.escena_actual.id == "E3"
    assert ids(sesion.opciones_disponibles()) == esperadas
    assert len(sesion.opciones_disponibles()) == 2  # exactamente dos en E3


def test_U1_condicion_false_se_evalua_por_igualdad(datos_validos):
    # Una condición {"x": false} debe cumplirse cuando x es false (no por "veracidad").
    s = Sesion(construir_historia(datos_validos))
    s.elegir("revisar"); s.elegir("continuar")
    assert "activar_sin_verificar" in ids(s.opciones_disponibles())


# ---------------- U2: elección válida aplica efectos y avanza
def test_U2_eleccion_valida_aplica_efectos_y_avanza(sesion):
    assert sesion.elegir("revisar").aceptada
    assert sesion.escena_actual.id == "E2"
    r = sesion.elegir("investigar")
    assert r.aceptada
    assert sesion.escena_actual.id == "E3"
    assert sesion.variables == {"conoce_origen": True, "confia_en_la_voz": False}


def test_CA01(sesion):
    sesion.elegir("revisar"); sesion.elegir("investigar")
    assert sesion.escena_actual.id == "E3" and sesion.variables["conoce_origen"] is True
    assert ids(sesion.opciones_disponibles()) == ["activar_codigo", "cortar"]


# ---------------- U3: opción inexistente o no habilitada deja intacto el estado
@pytest.mark.parametrize(
    "camino, intento",
    [
        ([], "no_existe"),                                  # opción inexistente
        (["revisar"], "revisar"),                           # ID de otra escena
        (["revisar", "continuar"], "activar_codigo"),       # CA02: no habilitada
        (["revisar", "investigar"], "activar_sin_verificar"),
        (["revisar", "continuar", "cortar"], "cortar"),     # elegir en escena final
        ([], ""),                                           # entrada vacía
    ],
    ids=["inexistente", "de_otra_escena", "CA02_activar_codigo", "sin_verificar_bloqueada", "en_final", "vacia"],
)
def test_U3_opcion_invalida_no_altera_estado(sesion, camino, intento):
    for op in camino:
        sesion.elegir(op)
    escena_antes, vars_antes = sesion.escena_actual.id, sesion.variables
    r = sesion.elegir(intento)
    assert r.aceptada is False and r.mensaje
    assert sesion.escena_actual.id == escena_antes
    assert sesion.variables == vars_antes


def test_CA02_sin_conocer_origen_activar_sin_verificar_lleva_a_E5(sesion):
    sesion.elegir("revisar"); sesion.elegir("continuar")
    assert not sesion.elegir("activar_codigo").aceptada
    assert sesion.elegir("activar_sin_verificar").aceptada
    assert sesion.escena_actual.id == "E5" and sesion.terminada


def test_variables_expuestas_son_copia(sesion):
    sesion.variables["conoce_origen"] = True
    assert sesion.variables["conoce_origen"] is False


# ---------------- U5: reiniciar restaura escena y variables iniciales
def test_U5_reiniciar_restaura_estado_inicial(sesion):
    sesion.elegir("revisar"); sesion.elegir("investigar"); sesion.elegir("activar_codigo")
    assert sesion.terminada and sesion.variables["confia_en_la_voz"] is True
    sesion.reiniciar()
    assert sesion.escena_actual.id == "E1"
    assert sesion.variables == {"conoce_origen": False, "confia_en_la_voz": False}
    # sin restos de la partida anterior: en E3 vuelve a verse "activar_sin_verificar"
    sesion.elegir("revisar"); sesion.elegir("continuar")
    assert ids(sesion.opciones_disponibles()) == ["activar_sin_verificar", "cortar"]


def test_U5_dos_sesiones_no_comparten_estado(sesion):
    from motor import cargar_historia
    from tests.conftest import RUTA_TRANSMISION
    h = cargar_historia(RUTA_TRANSMISION)
    a, b = Sesion(h), Sesion(h)
    a.elegir("revisar"); a.elegir("investigar")
    assert b.variables["conoce_origen"] is False
    assert h.variables_iniciales["conoce_origen"] is False
