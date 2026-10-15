"""Interfaz de consola. Uso: python jugar.py historias/la_ultima_transmision.json"""
from __future__ import annotations

import sys

from motor import ErrorContenido, Sesion, cargar_historia


def menu_cierre(sesion: Sesion, entrada=input) -> str:
    """Al final o en un bloqueo: 's' otra partida, 'n' salir, 'd' deshacer (si se puede)."""
    validas = ("s", "n", "d") if sesion.puede_deshacer else ("s", "n")
    texto = "¿Jugar otra partida? (s/n" + ("/d = deshacer última decisión" if sesion.puede_deshacer else "") + "): "
    while True:
        r = entrada(texto).strip().lower()
        if r in validas:
            return r
        print("Responda " + ", ".join(f"'{v}'" for v in validas) + ".")


def jugar(sesion: Sesion, entrada=input) -> None:
    while True:
        esc = sesion.escena_actual
        print(f"\n[{esc.id}] {esc.texto}")
        opciones = sesion.opciones_disponibles()
        if sesion.terminada or not opciones:
            if sesion.terminada:
                print("\n*** FIN DE LA HISTORIA ***")
            else:
                print("\n[BLOQUEO] Esta escena no tiene opciones habilitadas. Avise a la escritora: "
                      f"revise las condiciones de la escena '{esc.id}'.")
            r = menu_cierre(sesion, entrada)
            if r == "n":
                return
            if r == "d":
                print(sesion.deshacer().mensaje)
            else:
                sesion.reiniciar()
            continue
        for i, op in enumerate(opciones, 1):
            print(f"  {i}. {op.texto}")
        if sesion.puede_deshacer:
            print("  d. Deshacer la última decisión")
        sel = entrada("Elija una opción: ").strip().lower()
        if sel == "d":
            print(sesion.deshacer().mensaje)
            continue
        if not sel.isdigit() or not 1 <= int(sel) <= len(opciones):
            extra = " o 'd' para deshacer" if sesion.puede_deshacer else ""
            print(f"Entrada no válida: escriba un número entre 1 y {len(opciones)}{extra}.")
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
