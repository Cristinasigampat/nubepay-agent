"""
logging_agente.py

Registra cada ejecución del agente (pregunta, chunks usados, respuesta,
tiempo de respuesta) en un archivo local en formato JSON Lines --
una línea por pregunta, cada una un objeto JSON independiente.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

RUTA_LOG = Path(__file__).parent.parent.parent / "logs" / "ejecucion.jsonl"


def registrar_ejecucion(pregunta: str, resultado: dict, tiempo_ms: float) -> None:
    """
    Guarda una línea nueva en el archivo de log, con los datos de
    una ejecución del agente.
    """
    RUTA_LOG.parent.mkdir(parents=True, exist_ok=True)

    entrada = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "respuesta": resultado["respuesta"],
        "fuentes": resultado["fuentes"],
        "hubo_fallback": resultado["hubo_fallback"],
        "tiempo_ms": round(tiempo_ms, 2),
    }

    with open(RUTA_LOG, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(entrada, ensure_ascii=False) + "\n")


# --- Prueba rápida del módulo ---
if __name__ == "__main__":
    import sys
    import time

    sys.path.append(str(Path(__file__).parent))
    from rag_chain import responder

    preguntas_de_prueba = [
        "¿Cuánto puedo transferir por día?",
        "¿Cuál es la capital de Argentina?",
    ]

    for pregunta in preguntas_de_prueba:
        inicio = time.time()
        resultado = responder(pregunta)
        tiempo_ms = (time.time() - inicio) * 1000

        registrar_ejecucion(pregunta, resultado, tiempo_ms)
        print(f"Pregunta: {pregunta}")
        print(f"Tiempo: {tiempo_ms:.0f} ms")
        print(f"Registrado en: {RUTA_LOG}")
        print()

    print("--- Contenido del archivo de log ---")
    with open(RUTA_LOG, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            print(linea.strip())
