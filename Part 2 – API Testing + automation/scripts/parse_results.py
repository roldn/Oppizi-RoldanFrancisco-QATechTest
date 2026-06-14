#!/usr/bin/env python3
"""
Oppizi – OCM API Test Result Parser
Genera un resumen detallado desde el JSON de Newman con perspectiva QA Senior.
"""

import json
import sys
import os
from datetime import datetime, timezone

# ── ANSI Colors ──────────────────────────────────────────────────────────
R  = "\033[0;31m"   # red
G  = "\033[0;32m"   # green
Y  = "\033[1;33m"   # yellow
B  = "\033[0;34m"   # blue
C  = "\033[0;36m"   # cyan
M  = "\033[0;35m"   # magenta
BL = "\033[1m"      # bold
NC = "\033[0m"      # reset

def color_status(passed):
    return f"{G}PASS{NC}" if passed else f"{R}FAIL{NC}"

def ms_color(ms):
    if ms < 500:
        return f"{G}{ms}ms{NC}"
    elif ms < 900:
        return f"{Y}{ms}ms{NC}"
    else:
        return f"{R}{ms}ms ⚠{NC}"

def bar(passed, total, width=30):
    if total == 0:
        return "[" + "─" * width + "]"
    filled = int((passed / total) * width)
    empty  = width - filled
    pct    = (passed / total) * 100
    color  = G if pct == 100 else Y if pct >= 70 else R
    return f"{color}[{'█' * filled}{'░' * empty}] {pct:.0f}%{NC}"

def main():
    if len(sys.argv) < 2:
        print("Usage: parse_results.py <json_report> [run_id]")
        sys.exit(1)

    json_path = sys.argv[1]
    run_id    = sys.argv[2] if len(sys.argv) > 2 else "RUN"

    with open(json_path) as f:
        data = json.load(f)

    run   = data.get("run", {})
    stats = run.get("stats", {})
    times = run.get("timings", {})
    items = run.get("executions", [])
    info  = data.get("collection", {}).get("info", {})

    # ── Global stats ─────────────────────────────────────────────────────
    req_total  = stats.get("requests",   {}).get("total",  0)
    req_fail   = stats.get("requests",   {}).get("failed", 0)
    test_total = stats.get("assertions", {}).get("total",  0)
    test_fail  = stats.get("assertions", {}).get("failed", 0)
    test_pass  = test_total - test_fail
    duration_s = round((times.get("completed", 0) - times.get("started", 0)) / 1000, 2)
    avg_rt     = round(times.get("responseAverage", 0))

    pass_rate  = (test_pass / test_total * 100) if test_total else 0

    # ── Header ───────────────────────────────────────────────────────────
    print(f"\n{BL}{'═'*66}{NC}")
    print(f"{BL}  OPPIZI – OCM API TEST REPORT  |  {run_id}{NC}")
    print(f"{BL}{'═'*66}{NC}")
    print(f"  Colección  : {info.get('name', 'N/A')}")
    print(f"  Ejecutado  : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  Duración   : {duration_s}s  |  Avg response: {ms_color(avg_rt)}")
    print(f"{'─'*66}")

    # ── Global scorecard ─────────────────────────────────────────────────
    print(f"\n{BL}  SCORECARD GLOBAL{NC}")
    print(f"  Requests   : {req_total - req_fail}/{req_total} exitosos  {bar(req_total - req_fail, req_total)}")
    print(f"  Assertions : {test_pass}/{test_total} pasaron     {bar(test_pass, test_total)}")
    print(f"  Pass rate  : {G if pass_rate==100 else Y if pass_rate>=70 else R}{pass_rate:.1f}%{NC}")
    print()

    # ── Per-request breakdown ─────────────────────────────────────────────
    print(f"{BL}  DETALLE POR REQUEST{NC}")
    print(f"  {'ID':<8} {'Nombre':<48} {'RT':>7}  {'Result'}")
    print(f"  {'─'*8} {'─'*48} {'─'*7}  {'─'*6}")

    failures = []
    response_times = []
    categories = {}

    for exec_item in items:
        item      = exec_item.get("item", {})
        name      = item.get("name", "Unknown")
        response  = exec_item.get("response", {})
        asserts   = exec_item.get("assertions", [])

        rt        = response.get("responseTime", 0) if response else 0
        status    = response.get("status", "N/A") if response else "ERROR"
        code      = response.get("code", 0) if response else 0

        response_times.append(rt)

        # Category detection
        cat = "POI" if name.startswith("POI") else "REF" if name.startswith("REF") else "OTHER"
        if cat not in categories:
            categories[cat] = {"pass": 0, "fail": 0, "times": []}
        categories[cat]["times"].append(rt)

        # Assertion results
        failed_asserts = [a for a in asserts if a.get("error")]
        all_pass       = len(failed_asserts) == 0

        if all_pass:
            categories[cat]["pass"] += 1
        else:
            categories[cat]["fail"] += 1

        # Extract test ID from name
        tc_id = name.split("–")[0].strip() if "–" in name else name[:8]

        rt_str = f"{rt}ms"
        result_str = f"{G}✓ PASS{NC}" if all_pass else f"{R}✗ FAIL{NC}"
        print(f"  {tc_id:<8} {name[:48]:<48} {rt_str:>7}  {result_str}")

        if not all_pass:
            for fa in failed_asserts:
                err = fa.get("error", {})
                msg = err.get("message", "Unknown error")
                failures.append({
                    "tc": name,
                    "assertion": fa.get("assertion", "?"),
                    "message": msg
                })

    # ── Category breakdown ────────────────────────────────────────────────
    print(f"\n{BL}  BREAKDOWN POR CATEGORÍA{NC}")
    print(f"  {'Categoría':<12} {'Pass':<6} {'Fail':<6} {'Avg RT':<10} {'Barra'}")
    print(f"  {'─'*12} {'─'*6} {'─'*6} {'─'*10} {'─'*35}")
    for cat_name, cat_data in categories.items():
        total_cat = cat_data["pass"] + cat_data["fail"]
        avg_cat   = round(sum(cat_data["times"]) / len(cat_data["times"])) if cat_data["times"] else 0
        print(f"  {cat_name:<12} {cat_data['pass']:<6} {cat_data['fail']:<6} {avg_cat}ms{'':<6} {bar(cat_data['pass'], total_cat, 20)}")

    # ── Performance analysis ──────────────────────────────────────────────
    print(f"\n{BL}  ANÁLISIS DE PERFORMANCE{NC}")
    if response_times:
        sorted_rt = sorted(response_times)
        p50 = sorted_rt[len(sorted_rt) // 2]
        p90 = sorted_rt[int(len(sorted_rt) * 0.90)]
        p95 = sorted_rt[int(len(sorted_rt) * 0.95)]
        max_rt = max(sorted_rt)
        min_rt = min(sorted_rt)
        slow   = [rt for rt in response_times if rt > 900]
        print(f"  P50 (mediana)  : {ms_color(p50)}")
        print(f"  P90            : {ms_color(p90)}")
        print(f"  P95            : {ms_color(p95)}")
        print(f"  Más rápido     : {G}{min_rt}ms{NC}")
        print(f"  Más lento      : {ms_color(max_rt)}")
        print(f"  SLA <1000ms    : {'CUMPLIDO' if not slow else f'{R}VIOLADO en {len(slow)} request(s){NC}'}")
        if slow:
            print(f"  {Y}  ⚠ Requests que superaron 900ms: {slow}{NC}")

    # ── Failures detail ───────────────────────────────────────────────────
    if failures:
        print(f"\n{BL}  FALLOS DETECTADOS  ({len(failures)} assertion(s) fallida(s)){NC}")
        print(f"  {'─'*64}")
        for i, f in enumerate(failures, 1):
            print(f"\n  {R}[{i}] Test Case: {f['tc']}{NC}")
            print(f"      Assertion : {f['assertion']}")
            print(f"      Error     : {Y}{f['message']}{NC}")
            # QA Senior analysis
            tc_name = f["tc"].lower()
            if "401" in f["assertion"] or "401" in f["message"]:
                print(f"      {C}⚡ Análisis QA: La API retorna 200 en lugar de 401 para requests sin key.")
                print(f"         Esto indica que la validación de auth se hace upstream (gateway) y no")
                print(f"         en el endpoint directamente. Documentar como comportamiento conocido.{NC}")
            elif "response time" in f["assertion"].lower() or "1000" in f["message"]:
                print(f"      {C}⚡ Análisis QA: SLA de performance violado. Verificar carga del servidor,")
                print(f"         parámetros de búsqueda (maxresults alto), y latencia de red del CI.{NC}")
            elif "empty" in f["assertion"].lower():
                print(f"      {C}⚡ Análisis QA: Posible datos reales en coordenadas (0,0). Verificar si")
                print(f"         la API tiene estaciones registradas en el punto de origen null island.{NC}")
    else:
        print(f"\n  {G}✓ No se detectaron fallos en las assertions.{NC}")

    # ── QA Senior observations ────────────────────────────────────────────
    print(f"\n{BL}  OBSERVACIONES QA SENIOR{NC}")
    print(f"  {'─'*64}")

    obs = []

    if pass_rate == 100:
        obs.append(f"{G}✓ Pass rate 100%: la API se comporta según la especificación en todas las validaciones críticas.{NC}")
    elif pass_rate >= 80:
        obs.append(f"{Y}⚠ Pass rate {pass_rate:.0f}%: revisar fallos antes de release.{NC}")
    else:
        obs.append(f"{R}✗ Pass rate {pass_rate:.0f}%: bloqueante para producción.{NC}")

    if avg_rt < 500:
        obs.append(f"{G}✓ Performance excelente: avg {avg_rt}ms, muy por debajo del SLA de 1000ms.{NC}")
    elif avg_rt < 800:
        obs.append(f"{Y}⚠ Performance aceptable: avg {avg_rt}ms. Monitorear bajo carga.{NC}")
    else:
        obs.append(f"{R}✗ Performance degradada: avg {avg_rt}ms, cerca del límite SLA.{NC}")

    obs.append(f"{C}📋 REF-11 (referential integrity) es el test de mayor valor para Oppizi:")
    obs.append(f"   valida que los ConnectionTypeIDs del POI live existan en el catálogo de referencia.{NC}")
    obs.append(f"{C}📋 POI-08 (Haversine check) protege contra errores de geofencing del servidor.")
    obs.append(f"   Cualquier fallo aquí es un bug crítico para la lógica de campaña de Oppizi.{NC}")
    obs.append(f"{Y}📋 POI-12/REF-12 (missing key → 401): si fallan, NO son bloqueantes — es un")
    obs.append(f"   comportamiento documentado del gateway OCM. El fix debe ser en el edge de Oppizi.{NC}")

    for o in obs:
        print(f"  {o}")

    # ── Risk register ─────────────────────────────────────────────────────
    print(f"\n{BL}  RISK REGISTER POST-RUN{NC}")
    print(f"  {'─'*64}")
    risks = [
        ("ALTO",   "POI-12/REF-12: Auth no validada por OCM. Gateway de Oppizi debe interceptar."),
        ("MEDIO",  "POI-13: (0,0) puede tener datos reales — revisar si el assert de 0 resultados es correcto."),
        ("MEDIO",  "REF-11: Depende de datos live POI. Puede flakear si la zona no tiene estaciones."),
        ("BAJO",   "POI-08: Tolerancia Haversine al 5%. Ajustar si se requiere precisión sub-kilómetro."),
        ("BAJO",   "REF-10: IsOperational asume que OCM mantiene al menos 1 estado operacional siempre."),
    ]
    for level, desc in risks:
        color = R if level == "ALTO" else Y if level == "MEDIO" else G
        print(f"  {color}[{level}]{NC}  {desc}")

    # ── Footer ────────────────────────────────────────────────────────────
    overall = f"{G}✓ EXITOSO{NC}" if test_fail == 0 else f"{R}✗ CON FALLOS{NC}"
    print(f"\n{BL}{'═'*66}{NC}")
    print(f"{BL}  VEREDICTO FINAL: {NC}{overall}")
    print(f"  {test_pass}/{test_total} assertions  |  {duration_s}s  |  Run: {run_id}")
    print(f"{BL}{'═'*66}{NC}\n")

if __name__ == "__main__":
    main()
