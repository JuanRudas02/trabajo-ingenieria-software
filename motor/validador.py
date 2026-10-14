"""Validación del contrato de contenido ANTES de iniciar una partida (N06).

Recoge todos los errores encontrados en lugar de detenerse en el primero,
para que la escritora pueda corregir el archivo en una sola pasada.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .errores import ErrorValidacion

E = ErrorValidacion

CAMPOS_HISTORIA = {"titulo": str, "inicio": str, "variables": dict, "escenas": list}
CAMPOS_ESCENA = {"id": str, "texto": str, "final": bool, "opciones": list}
CAMPOS_OPCION = {"id": str, "texto": str, "destino": str, "condiciones": dict, "efectos": dict}


def _es_bool(valor: Any) -> bool:
    # En Python bool es subclase de int: 1 y 0 NO son booleanos válidos aquí.
    return type(valor) is bool


def _campos(obj: Any, esquema: Dict[str, type], ubic: str, errores: List[E]) -> bool:
    if not isinstance(obj, dict):
        errores.append(E("ESTRUCTURA_INVALIDA", "se esperaba un objeto", ubic))
        return False
    ok = True
    for nombre, tipo in esquema.items():
        if nombre not in obj:
            errores.append(E("CAMPO_FALTANTE", f"falta el campo obligatorio '{nombre}'", f"{ubic}.{nombre}"))
            ok = False
        elif tipo is bool and not _es_bool(obj[nombre]):
            errores.append(E("VALOR_NO_BOOLEANO", f"'{nombre}' debe ser true o false", f"{ubic}.{nombre}"))
            ok = False
        elif tipo is not bool and not isinstance(obj[nombre], tipo):
            errores.append(E("ESTRUCTURA_INVALIDA", f"'{nombre}' debe ser de tipo {tipo.__name__}", f"{ubic}.{nombre}"))
            ok = False
    return ok


def _mapa_booleano(mapa: Dict[str, Any], declaradas: Dict[str, Any], ubic: str, errores: List[E]) -> None:
    for var, valor in mapa.items():
        if var not in declaradas:
            errores.append(E("VARIABLE_NO_DECLARADA", f"la variable '{var}' no está declarada en 'variables'", f"{ubic}.{var}"))
        if not _es_bool(valor):
            errores.append(E("VALOR_NO_BOOLEANO", f"el valor de '{var}' debe ser true o false (recibido {valor!r})", f"{ubic}.{var}"))


def validar(datos: Any) -> List[E]:
    errores: List[E] = []
    if not _campos(datos, CAMPOS_HISTORIA, "historia", errores):
        return errores

    variables = datos["variables"]
    for var, valor in variables.items():
        if not _es_bool(valor):
            errores.append(E("VALOR_NO_BOOLEANO", f"el valor inicial de '{var}' debe ser true o false", f"variables.{var}"))

    if not datos["escenas"]:
        errores.append(E("ESTRUCTURA_INVALIDA", "la historia debe tener al menos una escena", "escenas"))

    ids_escena: set[str] = set()
    escenas_validas = []
    for i, esc in enumerate(datos["escenas"]):
        ubic = f"escenas[{i}]"
        if not _campos(esc, CAMPOS_ESCENA, ubic, errores):
            continue
        ubic = f"escena {esc['id']}"
        if esc["id"] in ids_escena:
            errores.append(E("ID_ESCENA_DUPLICADO", f"el ID de escena '{esc['id']}' está repetido", ubic))
        ids_escena.add(esc["id"])
        escenas_validas.append(esc)

        n = len(esc["opciones"])
        if esc["final"] and n > 0:
            errores.append(E("OPCIONES_INCOMPATIBLES_FINAL", f"una escena final debe tener 0 opciones (tiene {n})", ubic))
        if not esc["final"] and n == 0:
            errores.append(E("OPCIONES_INCOMPATIBLES_FINAL", "una escena no final debe tener al menos una opción", ubic))

    if datos["inicio"] not in ids_escena:
        errores.append(E("INICIO_INEXISTENTE", f"la escena inicial '{datos['inicio']}' no existe", "inicio"))

    for esc in escenas_validas:
        ids_opcion: set[str] = set()  # ámbito: la escena (el mismo ID puede repetirse en otra escena)
        for j, op in enumerate(esc["opciones"]):
            ubic = f"escena {esc['id']}.opciones[{j}]"
            if not _campos(op, CAMPOS_OPCION, ubic, errores):
                continue
            ubic = f"escena {esc['id']}.opcion {op['id']}"
            if op["id"] in ids_opcion:
                errores.append(E("ID_OPCION_DUPLICADO", f"el ID de opción '{op['id']}' está repetido en la escena", ubic))
            ids_opcion.add(op["id"])
            if op["destino"] not in ids_escena:
                errores.append(E("DESTINO_INEXISTENTE", f"el destino '{op['destino']}' no existe", f"{ubic}.destino"))
            _mapa_booleano(op["condiciones"], variables, f"{ubic}.condiciones", errores)
            _mapa_booleano(op["efectos"], variables, f"{ubic}.efectos", errores)
    return errores
