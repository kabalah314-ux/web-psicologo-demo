#!/usr/bin/env python
"""Ejecuta los criterios de la fase actual.
Uso: python HARNESS/check.py [--fase N] [--con-red]
  --fase N   fuerza una fase concreta (no actualiza STATE.md si N != FASE_ACTUAL)
  --con-red  permite checks que usan red real (OpenRouter, Telegram). Gastan cupo. Solo si lo pide el humano.
"""
import sys, re, importlib, datetime, pathlib, traceback, os
RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "backend")); sys.path.insert(0, str(RAIZ / "HARNESS"))
os.chdir(RAIZ / "backend") if (RAIZ / "backend").exists() else os.chdir(RAIZ)
STATE = RAIZ / "HARNESS" / "STATE.md"
NOMBRES = ["Esqueleto y arnés", "Motor de agenda", "API pública + notificaciones",
           "API admin + tareas", "Frontend", "Chat IA", "Operación y despliegue"]

def leer_fase():
    m = re.search(r"FASE_ACTUAL:\s*(\d+)", STATE.read_text(encoding="utf-8"))
    return int(m.group(1)) if m else 0

def escribir_estado(fase, resultados, completada):
    txt = STATE.read_text(encoding="utf-8")
    if completada:
        txt = txt.replace(f"- [ ] Fase {fase} —", f"- [x] Fase {fase} —")
        txt = re.sub(r"FASE_ACTUAL:\s*\d+", f"FASE_ACTUAL: {min(fase + 1, 6)}", txt)
    lineas = [f"{datetime.datetime.now():%Y-%m-%d %H:%M} · Fase {fase} · " + ("COMPLETADA" if completada else "EN CURSO")]
    lineas += [f"- {'PASS' if ok else 'FAIL'} · {n}" + ("" if ok else f" -> {str(msg)[:300]}") for n, ok, msg in resultados]
    bloque = "## Último check\n" + "\n".join(lineas) + "\n"
    txt = re.sub(r"## Último check\n.*?(?=\n## NOTAS)", lambda m: bloque, txt, flags=re.S)
    STATE.write_text(txt, encoding="utf-8")

def main():
    if "--con-red" in sys.argv: os.environ["HARNESS_CON_RED"] = "1"
    fase_actual = leer_fase()
    fase = int(sys.argv[sys.argv.index("--fase") + 1]) if "--fase" in sys.argv else fase_actual
    print(f"\n=== CHECK FASE {fase} — {NOMBRES[fase]} ===\n")
    try:
        mod = importlib.import_module(f"checks.fase{fase}")
    except Exception:
        print(f"No se pudo importar checks/fase{fase}.py:\n{traceback.format_exc()}"); sys.exit(2)
    resultados = []
    for nombre, fn in mod.CRITERIOS:
        try:
            ok, msg = fn()
        except Exception as e:
            ok, msg = False, f"excepción {type(e).__name__}: {e}"
        resultados.append((nombre, ok, msg))
        print(f"[{'PASS' if ok else 'FAIL'}] {nombre}" + ("" if ok else f"\n       → {str(msg)[:1500]}"))
    completada = all(ok for _, ok, _ in resultados)
    if fase == fase_actual: escribir_estado(fase, resultados, completada)
    fallos = sum(not ok for _, ok, _ in resultados)
    print("\n" + (f"✅ FASE {fase} COMPLETADA. Haz commit: git add -A && git commit -m 'fase-0{fase}: done'. Siguiente: fase {fase + 1}."
                  if completada else f"❌ {fallos} criterio(s) en FAIL. Arregla el PRIMERO y vuelve a ejecutar."))
    sys.exit(0 if completada else 1)

if __name__ == "__main__":
    main()