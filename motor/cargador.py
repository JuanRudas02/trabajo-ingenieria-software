"""Lectura de archivos de historia y construcción del modelo (capa de contenido)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Tuple

from .errores import ErrorContenido, ErrorValidacion
from .modelo import Escena, Historia, Opcion
from .validador import validar


def _sin_claves_duplicadas(pares: List[Tuple[str, Any]]) -> dict:
    # json estándar se queda en silencio con la última clave repetida; aquí se rechaza.
    resultado: dict = {}
    for clave, valor in pares:
        if clave in resultado:
            raise ValueError(f"clave JSON repetida '{clave}'")
        resultado[clave] = valor
    return resultado


def leer_json(ruta: str | Path) -> Any:
    try:
        texto = Path(ruta).read_text(encoding="utf-8")
    except OSError as exc:
        raise ErrorContenido([ErrorValidacion("ARCHIVO_ILEGIBLE", f"no se pudo abrir el archivo ({exc.strerror})", str(ruta))])
    try:
        return json.loads(texto, object_pairs_hook=_sin_claves_duplicadas)
    except json.JSONDecodeError as exc:
        raise ErrorContenido([ErrorValidacion("ARCHIVO_ILEGIBLE", f"JSON mal formado: {exc.msg}", f"línea {exc.lineno}, columna {exc.colno}")])
    except ValueError as exc:
        raise ErrorContenido([ErrorValidacion("ESTRUCTURA_INVALIDA", str(exc), str(ruta))])


def construir_historia(datos: Any) -> Historia:
    errores = validar(datos)
    if errores:
        raise ErrorContenido(errores)
    escenas = {
        e["id"]: Escena(
            id=e["id"], texto=e["texto"], final=e["final"],
            opciones=tuple(Opcion(o["id"], o["texto"], o["destino"], dict(o["condiciones"]), dict(o["efectos"]))
                           for o in e["opciones"]),
        )
        for e in datos["escenas"]
    }
    return Historia(datos["titulo"], datos["inicio"], dict(datos["variables"]), escenas)


def cargar_historia(ruta: str | Path) -> Historia:
    """Lee, valida y construye una historia. Lanza ErrorContenido si es inválida."""
    return construir_historia(leer_json(ruta))
