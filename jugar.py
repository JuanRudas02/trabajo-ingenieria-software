"""Interfaz de consola. Uso: python jugar.py historias/la_ultima_transmision.json"""
from __future__ import annotations

import sys

from motor import ErrorContenido, Sesion, cargar_historia


def preguntar_reinicio(entrada=input) -> bool:
    while True:
        r = entrada("¿Jugar otra partida? (s/n): ").strip().lower()
        if r in ("s", "n"):
            return r == "s"
        print("Responda 's' o 'n'.")


def jugar(sesion: Sesion, entrada=input) -> None:
    while True:
        esc = sesion.escena_actual
        print(f"\n[{esc.id}] {esc.texto}")
        if sesion.terminada:
            print("\n*** FIN DE LA HISTORIA ***")
            if not preguntar_reinicio(entrada):
                return
            sesion.reiniciar()
            continue
        opciones = sesion.opciones_disponibles()
        if not opciones:
            print("\n[BLOQUEO] Esta escena no tiene opciones habilitadas. Avise a la escritora: "
                  f"revise las condiciones de la escena '{esc.id}'.")
            if not preguntar_reinicio(entrada):
                return
            sesion.reiniciar()
            continue
        for i, op in enumerate(opciones, 1):
            print(f"  {i}. {op.texto}")
        sel = entrada("Elija un número: ").strip()
        if not sel.isdigit() or not 1 <= int(sel) <= len(opciones):
            print(f"Entrada no válida: escriba un número entre 1 y {len(opciones)}.")
            continue
        sesion.elegir(opciones[int(sel) - 1].id)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Uso: python jugar.py <ruta_historia.json>")
        return 2
    try:
        historia = cargar_historia(argv[1])
    except ErrorContenido as exc:
        print(exc)
        return 1
    print(f"=== {historia.titulo} ===")
    try:
        jugar(Sesion(historia))
    except (EOFError, KeyboardInterrupt):
        print("\nPartida finalizada por el usuario.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
