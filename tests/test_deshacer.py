"""U6 (solicitud de cambio de la hora 6): deshacer la última decisión, un solo nivel."""
import pytest

from motor import Sesion, construir_historia


def ids(opciones):
    return [o.id for o in opciones]


def estado(s):
    return s.escena_actual.id, s.variables, s.puede_deshacer


# ---------------- U6: deshacer restaura escena y variables y consume el retroceso
def test_U6_ejemplo_de_la_solicitud(sesion):
    """Desde E2, investigar lleva a E3 con conoce_origen verdadero; deshacer vuelve a E2
    con conoce_origen falso; un segundo deshacer no cambia nada; al continuar sin
    investigar, E3 muestra activar sin verificar y cortar comunicación."""
    sesion.elegir("revisar")
    assert sesion.elegir("investigar").aceptada
    assert sesion.escena_actual.id == "E3" and sesion.variables["conoce_origen"] is True

    r = sesion.deshacer()
    assert r.aceptada
    assert sesion.escena_actual.id == "E2"
    assert sesion.variables == {"conoce_origen": False, "confia_en_la_voz": False}
    assert sesion.puede_deshacer is False

    antes = estado(sesion)
    r2 = sesion.deshacer()
    assert r2.aceptada is False and r2.mensaje
    assert estado(sesion) == antes

    sesion.elegir("continuar")
    assert ids(sesion.opciones_disponibles()) == ["activar_sin_verificar", "cortar"]


@pytest.mark.parametrize(
    "camino, escena_previa, vars_previas",
    [
        (["revisar"], "E1", {"conoce_origen": False, "confia_en_la_voz": False}),
        (["revisar", "investigar"], "E2", {"conoce_origen": False, "confia_en_la_voz": False}),
        (["revisar", "investigar", "activar_codigo"], "E3", {"conoce_origen": True, "confia_en_la_voz": False}),
    ],
    ids=["desde_E2", "desde_E3", "desde_final_E4"],
)
def test_U6_restaura_exactamente_el_estado_previo(sesion, camino, escena_previa, vars_previas):
    for op in camino:
        sesion.elegir(op)
    assert sesion.deshacer().aceptada
    assert sesion.escena_actual.id == escena_previa
    assert sesion.variables == vars_previas
    assert not sesion.puede_deshacer


def test_U6_al_comenzar_no_hay_retroceso(sesion):
    antes = estado(sesion)
    assert sesion.puede_deshacer is False
    assert sesion.deshacer().aceptada is False
    assert estado(sesion) == antes


@pytest.mark.parametrize(
    "intento",
    ["no_existe", "activar_sin_verificar", "revisar", ""],
    ids=["inexistente", "no_habilitada", "de_otra_escena", "vacia"],
)
def test_U6_entrada_invalida_preserva_el_historial(sesion, intento):
    sesion.elegir("revisar"); sesion.elegir("investigar")       # E3, conoce_origen = true
    assert sesion.elegir(intento).aceptada is False
    assert sesion.puede_deshacer
    sesion.deshacer()
    assert sesion.escena_actual.id == "E2"                      # deshace 'investigar', no el intento inválido
    assert sesion.variables["conoce_origen"] is False


def test_U6_nueva_eleccion_vuelve_a_habilitar_el_retroceso(sesion):
    sesion.elegir("revisar"); sesion.elegir("investigar")
    sesion.deshacer()
    assert not sesion.puede_deshacer
    assert sesion.elegir("continuar").aceptada
    assert sesion.puede_deshacer
    sesion.deshacer()
    assert sesion.escena_actual.id == "E2"


def test_U6_un_solo_nivel_no_encadena_retrocesos(sesion):
    sesion.elegir("revisar"); sesion.elegir("investigar")
    sesion.deshacer()                   # vuelve a E2
    assert not sesion.deshacer().aceptada
    assert sesion.escena_actual.id == "E2"   # no retrocede a E1


def test_U6_deshacer_desde_bloqueo(datos_validos):
    datos_validos["escenas"][2]["opciones"] = [datos_validos["escenas"][2]["opciones"][0]]  # solo activar_codigo
    s = Sesion(construir_historia(datos_validos))
    s.elegir("revisar"); s.elegir("continuar")
    assert s.bloqueada
    s.deshacer(); s.elegir("investigar")
    assert not s.bloqueada and [o.id for o in s.opciones_disponibles()] == ["activar_codigo"]
