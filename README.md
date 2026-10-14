# La última transmisión: motor de historias interactivas

**Autor:** Juan Manuel Rudas Tijera (T00067552)  
**Asignatura:** Ingeniería de Software, parcial práctico  
**Docente:** Aisner Marrugo  
**Repositorio:** https://github.com/JuanRudas02/trabajo-ingenieria-software

## Versiones requeridas
- Python 3.10 o superior (probado con 3.13)
- pytest 8 o superior, probado con 9.1 (única dependencia externa, licencia MIT, solo para pruebas)

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución
```bash
python jugar.py historias/la_ultima_transmision.json
python jugar.py historias/el_faro.json          # segunda historia, mismo motor
```
Se elige escribiendo el número de la opción. Al llegar a un final, el programa pregunta si se desea otra partida (`s`/`n`).

## Pruebas
```bash
python -m pytest -v                 # toda la suite
python -m pytest -v > resultados/ultima_ejecucion.txt
```
| Archivo | Cubre |
|---|---|
| `tests/test_sesion.py` | U1, U2, U3, U5, CA01, CA02 |
| `tests/test_validacion.py` | U4 (9 categorías de error), CA03, bloqueo en ejecución |
| `tests/test_integracion.py` | I1 (tres finales con archivo real, consola de extremo a extremo, segunda historia) |
| `tests/test_rnf.py` | RNF01, RNF02, RNF03 |

## Rutas para demostrar cada final (historia de referencia)
| Final | Entradas en consola | IDs de opción |
|---|---|---|
| E4 Rescate | `1, 1, 1` | revisar → investigar → activar_codigo |
| E5 El eco | `1, 2, 1` | revisar → continuar → activar_sin_verificar |
| E6 Silencio | `1, 1, 2` o `1, 2, 2` | revisar → (investigar \| continuar) → cortar |

Error de destino inexistente: copie la historia, cambie un `destino` por `E99` y ejecútela; el programa termina con código 1 y el mensaje
`[DESTINO_INEXISTENTE] escena E3.opcion cortar.destino: el destino 'E99' no existe`.

## Formato de contenido
Se usa el contrato JSON de la guía sin cambios:

| Elemento | Campos (todos obligatorios) |
|---|---|
| Historia | `titulo` (texto), `inicio` (ID de escena), `variables` (mapa nombre → `true`/`false`), `escenas` (lista) |
| Escena | `id` (único), `texto`, `final` (`true`/`false`), `opciones` (lista; vacía si es final) |
| Opción | `id` (único dentro de la escena), `texto`, `destino` (ID existente), `condiciones` (mapa variable → booleano), `efectos` (mapa variable → booleano) |

Reglas: una opción se muestra solo si **todas** sus condiciones son iguales al valor actual (`{}` = siempre visible). Al elegirla se aplican sus efectos y se pasa al destino. Los campos adicionales no previstos se ignoran (sirven para notas de la escritora). `condiciones` y `efectos` deben escribirse aunque estén vacíos (`{}`).

Para escribir una historia nueva: copie `historias/el_faro.json`, edítela y ejecútela con `python jugar.py <ruta>`. Si tiene errores, el programa los lista todos con su ubicación antes de empezar.

## Estructura
```
motor/        modelo.py (dominio) · validador.py · cargador.py (contenido) · sesion.py (reglas) · errores.py
jugar.py      interfaz de consola
historias/    la_ultima_transmision.json · el_faro.json
tests/        pruebas automatizadas
docs/         informe con anexos (main.tex para Overleaf y PDF)
```

## Limitaciones conocidas
- No hay retroceso (acuerdo provisional, ver informe §4).
- No se analiza estáticamente si todos los finales son alcanzables; los bloqueos se detectan durante la partida.
- No se guarda la partida entre ejecuciones (fuera de alcance).

## Fuentes y herramientas
- pytest (MIT) para pruebas. Biblioteca estándar de Python (`json`, `dataclasses`, `pathlib`).
- Asistente de IA (Claude, de Anthropic): primer borrador del código, las pruebas, los diagramas y el informe. Verificado ejecutando la suite completa y recorriendo a mano los tres finales y la segunda historia.
