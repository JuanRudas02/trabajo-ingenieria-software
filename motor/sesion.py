"""Reglas de juego: estado de una partida (capa de reglas, sin E/S)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .modelo import Escena, Historia, Opcion


@dataclass(frozen=True)
class ResultadoEleccion:
    aceptada: bool
    mensaje: str


class Sesion:
    """Una partida. No conoce IDs concretos de ninguna historia."""

    def __init__(self, historia: Historia):
        self._historia = historia
        self.reiniciar()

    # --- consultas -------------------------------------------------------
    @property
    def escena_actual(self) -> Escena:
        return self._historia.escena(self._id_escena)

    @property
    def variables(self) -> Dict[str, bool]:
        return dict(self._variables)  # copia: el exterior no puede alterar el estado

    @property
    def terminada(self) -> bool:
        return self.escena_actual.final

    @property
    def bloqueada(self) -> bool:
        """Escena no final sin ninguna opción habilitada (detectado en ejecución)."""
        return not self.terminada and not self.opciones_disponibles()

    def opciones_disponibles(self) -> List[Opcion]:
        return [o for o in self.escena_actual.opciones if o.habilitada(self._variables)]

    # --- comandos --------------------------------------------------------
    def elegir(self, id_opcion: str) -> ResultadoEleccion:
        """Valida primero; solo si es válida aplica efectos y avanza (atómico)."""
        if self.terminada:
            return ResultadoEleccion(False, "La partida terminó: reinicie para jugar de nuevo.")
        opcion = self.escena_actual.buscar_opcion(id_opcion)
        if opcion is None:
            return ResultadoEleccion(False, f"La opción '{id_opcion}' no existe en esta escena.")
        if not opcion.habilitada(self._variables):
            return ResultadoEleccion(False, f"La opción '{id_opcion}' no está disponible ahora.")
        nuevas = dict(self._variables)
        nuevas.update(opcion.efectos)
        self._variables = nuevas
        self._id_escena = opcion.destino
        return ResultadoEleccion(True, opcion.texto)

    def reiniciar(self) -> None:
        self._id_escena = self._historia.inicio
        self._variables = dict(self._historia.variables_iniciales)  # copia nueva, sin restos
