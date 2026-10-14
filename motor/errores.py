"""Errores de contenido con causa y ubicación identificables."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ErrorValidacion:
    codigo: str      # categoría del error (p. ej. DESTINO_INEXISTENTE)
    mensaje: str     # causa legible para la escritora
    ubicacion: str   # campo o ID involucrado (p. ej. escenas[2].opciones[0].destino)

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.ubicacion}: {self.mensaje}"


class ErrorContenido(Exception):
    """Se lanza cuando una historia no puede cargarse. Nunca se abre sesión."""

    def __init__(self, errores: List[ErrorValidacion]):
        self.errores = errores
        super().__init__("Historia inválida:\n" + "\n".join(f"  - {e}" for e in errores))
