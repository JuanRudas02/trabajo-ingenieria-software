"""U4: errores de contenido -> rechazo controlado (9 categorías) y CA03."""
import pytest

from motor import ErrorContenido, Sesion, cargar_historia, construir_historia


def _quitar(d, *ruta):
    obj = d
    for k in ruta[:-1]:
        obj = obj[k]
    del obj[ruta[-1]]


# Cada caso: (nombre, mutación, código esperado, texto que debe aparecer en la ubicación)
CASOS = [
    ("falta_titulo",          lambda d: _quitar(d, "titulo"),                                       "CAMPO_FALTANTE",        "titulo"),
    ("falta_escenas",         lambda d: _quitar(d, "escenas"),                                      "CAMPO_FALTANTE",        "escenas"),
    ("falta_destino",         lambda d: _quitar(d, "escenas", 0, "opciones", 0, "destino"),         "CAMPO_FALTANTE",        "destino"),
    ("falta_final",           lambda d: _quitar(d, "escenas", 3, "final"),                          "CAMPO_FALTANTE",        "final"),
    ("raiz_no_objeto",        lambda d: d.clear() or d.update({"x": 1}),                            "CAMPO_FALTANTE",        "titulo"),
    ("escenas_no_lista",      lambda d: d.update(escenas={}),                                       "ESTRUCTURA_INVALIDA",   "escenas"),
    ("inicio_inexistente",    lambda d: d.update(inicio="E0"),                                      "INICIO_INEXISTENTE",    "inicio"),
    ("escena_duplicada",      lambda d: d["escenas"][1].update(id="E1"),                            "ID_ESCENA_DUPLICADO",   "E1"),
    ("opcion_duplicada",      lambda d: d["escenas"][1]["opciones"][1].update(id="investigar"),     "ID_OPCION_DUPLICADO",   "investigar"),
    ("destino_E99",           lambda d: d["escenas"][0]["opciones"][0].update(destino="E99"),       "DESTINO_INEXISTENTE",   "revisar"),
    ("condicion_no_declarada",lambda d: d["escenas"][2]["opciones"][0]["condiciones"].update(x=True), "VARIABLE_NO_DECLARADA", "x"),
    ("efecto_no_declarado",   lambda d: d["escenas"][1]["opciones"][0]["efectos"].update(y=False),  "VARIABLE_NO_DECLARADA", "y"),
    ("condicion_texto",       lambda d: d["escenas"][2]["opciones"][0]["condiciones"].update(conoce_origen="true"), "VALOR_NO_BOOLEANO", "conoce_origen"),
    ("efecto_entero",         lambda d: d["escenas"][1]["opciones"][0]["efectos"].update(conoce_origen=1), "VALOR_NO_BOOLEANO", "conoce_origen"),
    ("variable_inicial_texto",lambda d: d["variables"].update(conoce_origen="no"),                  "VALOR_NO_BOOLEANO",     "variables.conoce_origen"),
    ("final_no_booleano",     lambda d: d["escenas"][3].update(final="si"),                         "VALOR_NO_BOOLEANO",     "final"),
    ("final_con_opciones",    lambda d: d["escenas"][3].update(opciones=[d["escenas"][0]["opciones"][0]]), "OPCIONES_INCOMPATIBLES_FINAL", "E4"),
    ("no_final_sin_opciones", lambda d: d["escenas"][1].update(opciones=[]),                        "OPCIONES_INCOMPATIBLES_FINAL", "E2"),
]


@pytest.mark.parametrize("mutar, codigo, ubicacion", [c[1:] for c in CASOS], ids=[c[0] for c in CASOS])
def test_U4_errores_de_contenido_se_rechazan(datos_validos, mutar, codigo, ubicacion):
    mutar(datos_validos)
    with pytest.raises(ErrorContenido) as exc:
        construir_historia(datos_validos)
    errores = exc.value.errores
    assert any(e.codigo == codigo and ubicacion in e.ubicacion for e in errores), errores
    assert all(e.mensaje for e in errores)


def test_mismo_id_de_opcion_en_escenas_distintas_es_valido(datos_validos):
    datos_validos["escenas"][1]["opciones"][1]["id"] = "revisar"  # 'revisar' también existe en E1
    construir_historia(datos_validos)  # no debe lanzar


def test_variable_sin_uso_en_condiciones_es_valida(datos_validos):
    # confia_en_la_voz solo aparece en efectos: no es un error.
    construir_historia(datos_validos)


@pytest.mark.parametrize(
    "contenido, codigo",
    [("{ esto no es json", "ARCHIVO_ILEGIBLE"),
     ('{"titulo": "a", "titulo": "b"}', "ESTRUCTURA_INVALIDA"),
     ("[1, 2, 3]", "ESTRUCTURA_INVALIDA")],
    ids=["json_mal_formado", "clave_repetida", "raiz_lista"],
)
def test_U4_archivo_ilegible_o_estructura(tmp_path, contenido, codigo):
    ruta = tmp_path / "h.json"
    ruta.write_text(contenido, encoding="utf-8")
    with pytest.raises(ErrorContenido) as exc:
        cargar_historia(ruta)
    assert exc.value.errores[0].codigo == codigo


def test_U4_archivo_inexistente(tmp_path):
    with pytest.raises(ErrorContenido) as exc:
        cargar_historia(tmp_path / "no_existe.json")
    assert exc.value.errores[0].codigo == "ARCHIVO_ILEGIBLE"


def test_CA03_destino_E99_rechaza_carga_sin_sesion(tmp_path, datos_validos):
    import json
    datos_validos["escenas"][2]["opciones"][2]["destino"] = "E99"
    ruta = tmp_path / "copia.json"
    ruta.write_text(json.dumps(datos_validos), encoding="utf-8")
    historia = None
    with pytest.raises(ErrorContenido) as exc:
        historia = cargar_historia(ruta)
    assert historia is None  # no se abre sesión jugable
    assert "E99" in str(exc.value) and "cortar" in str(exc.value)


def test_bloqueo_en_ejecucion_se_informa_y_permite_reiniciar(datos_validos):
    # Escena no final cuyas opciones exigen algo imposible en ese camino.
    datos_validos["escenas"][2]["opciones"] = [datos_validos["escenas"][2]["opciones"][0]]  # solo activar_codigo
    s = Sesion(construir_historia(datos_validos))
    s.elegir("revisar"); s.elegir("continuar")
    assert s.bloqueada and s.opciones_disponibles() == []
    s.reiniciar()
    assert s.escena_actual.id == "E1" and not s.bloqueada
