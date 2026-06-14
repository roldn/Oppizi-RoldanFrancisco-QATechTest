#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
#  Oppizi – OCM API Test Automation Runner
#  Ejecuta todos los tests y genera el reporte HTML profesional
# ═══════════════════════════════════════════════════════════════════════

set -e

# ── Colors ──────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

# ── Config ───────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTS_DIR="$SCRIPT_DIR/reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RUN_ID="OCM_RUN_$TIMESTAMP"

JSON_REPORT="$REPORTS_DIR/${RUN_ID}_results.json"
CUSTOM_HTML="$REPORTS_DIR/${RUN_ID}_custom_report.html"
SUMMARY_FILE="$REPORTS_DIR/${RUN_ID}_summary.txt"

# ── Banner ───────────────────────────────────────────────────────────────
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       OPPIZI – Open Charge Map API Test Automation          ║${NC}"
echo -e "${BLUE}║                   QA Automation Runner v1.0                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ── Find collection and environment files automatically ──────────────────
COLLECTION=$(find "$SCRIPT_DIR" -maxdepth 1 -name "*.postman_collection.json" | head -1)
ENVIRONMENT=$(find "$SCRIPT_DIR" -maxdepth 1 -name "*.postman_environment.json" | head -1)

if [ -z "$COLLECTION" ]; then
  echo -e "${RED}✗ No se encontró ningún archivo .postman_collection.json en esta carpeta.${NC}"
  exit 1
fi
if [ -z "$ENVIRONMENT" ]; then
  echo -e "${RED}✗ No se encontró ningún archivo .postman_environment.json en esta carpeta.${NC}"
  exit 1
fi

# ── Validate API key ─────────────────────────────────────────────────────
API_KEY="${OCM_API_KEY:-}"

if [ -z "$API_KEY" ]; then
  echo -e "${YELLOW}⚠  No se encontró la API key.${NC}"
  echo -e "${CYAN}   Ingresá tu API key de Open Charge Map:${NC} "
  read -r API_KEY
  if [ -z "$API_KEY" ]; then
    echo -e "${RED}✗ Error: La API key es requerida. Abortando.${NC}"
    exit 1
  fi
fi

echo -e "${GREEN}✓ API key configurada${NC}"

# ── Validate dependencies ────────────────────────────────────────────────
echo ""
echo -e "${BOLD}Verificando dependencias...${NC}"

if ! command -v newman &> /dev/null; then
  echo -e "${RED}✗ Newman no encontrado. Instalando...${NC}"
  npm install -g newman newman-reporter-htmlextra
fi

if ! command -v python3 &> /dev/null; then
  echo -e "${RED}✗ Python3 no encontrado. Instalá Python desde https://python.org${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Newman   : $(newman --version)${NC}"
echo -e "${GREEN}✓ Colección: $(basename "$COLLECTION")${NC}"
echo -e "${GREEN}✓ Ambiente : $(basename "$ENVIRONMENT")${NC}"

# ── Create reports directory ─────────────────────────────────────────────
mkdir -p "$REPORTS_DIR"

# ── Pre-run info ─────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}  Run ID    :${NC} $RUN_ID"
echo -e "${BOLD}  Timestamp :${NC} $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}▶  Ejecutando tests...${NC}"
echo ""

# ── Run Newman ───────────────────────────────────────────────────────────
set +e
newman run "$COLLECTION" \
  --environment "$ENVIRONMENT" \
  --env-var "apiKey=$API_KEY" \
  --reporters cli,json \
  --reporter-json-export "$JSON_REPORT" \
  --delay-request 400 \
  --timeout-request 8000 \
  2>&1 | tee "$SUMMARY_FILE"
NEWMAN_EXIT=${PIPESTATUS[0]}
set -e

# ── Generate custom HTML report ──────────────────────────────────────────
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}  GENERANDO REPORTE...${NC}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "$JSON_REPORT" ]; then
  python3 "$SCRIPT_DIR/scripts/generate_report.py" "$JSON_REPORT" "$CUSTOM_HTML" "$RUN_ID"
  echo -e "${GREEN}✓ Reporte HTML generado${NC}"
else
  echo -e "${RED}✗ No se encontró el archivo de resultados JSON.${NC}"
  exit 1
fi

# ── QA Summary in terminal ───────────────────────────────────────────────
echo ""
python3 "$SCRIPT_DIR/scripts/parse_results.py" "$JSON_REPORT" "$RUN_ID"

# ── Output locations ─────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}📁 Archivos generados:${NC}"
echo -e "   Reporte HTML → ${CYAN}$CUSTOM_HTML${NC}"
echo -e "   JSON raw     → ${CYAN}$JSON_REPORT${NC}"
echo ""

# ── Open custom HTML report automatically ───────────────────────────────
if command -v open &> /dev/null; then
  open "$CUSTOM_HTML"
elif command -v xdg-open &> /dev/null; then
  xdg-open "$CUSTOM_HTML"
fi

if [ "$NEWMAN_EXIT" -ne 0 ]; then
  echo -e "${YELLOW}⚠  Algunos tests fallaron. Revisá el reporte HTML para el detalle.${NC}"
else
  echo -e "${GREEN}✓ Ejecución completada.${NC}"
fi
