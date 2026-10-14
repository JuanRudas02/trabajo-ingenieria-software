"""Modelo de dominio inmutable de una historia interactiva (capa de contenido)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass(frozen=True)
class Opcion:
    id: str
    texto: str
    destino: str
    condiciones: Dict[str, bool] = field(default_factory=dict)
    efectos: Dict[str, bool] = field(default_factory=dict)

    def habilitada(self, variables: Dict[str, bool]) -> bool:
        """Todas las condiciones deben cumplirse por IGUALDAD (no por veracidad)."""
        return all(variables.get(k) == v for k, v in self.condiciones.items())


@dataclass(frozen=True)
class Escena:
    id: str
    texto: str
    final: bool
    opciones: Tuple[Opcion, ...] = ()

    def buscar_opcion(self, id_opcion: str) -> Opcion | None:
        return next((o for o in self.opciones if o.id == id_opcion), None)


@dataclass(frozen=True)
class Historia:
    titulo: str
    inicio: str
    variables_iniciales: Dict[str, bool]
    escenas: Dict[str, Escena]

    def escena(self, id_escena: str) -> Escena:
        return self.escenas[id_escena]
