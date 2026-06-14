# Oppizi – Open Charge Map API Test Suite
### Part 2 – API Testing + Automation

---

## ¿Qué hay en esta carpeta?

```
Part 2 – API Testing + Automation/
│
├── Oppizi – Open Charge Map API Tests.postman_collection.json   ← los 25 tests
├── Oppizi – OCM API (Environment).postman_environment.json      ← variables de entorno
├── run_tests.sh          ← script de ejecución automática (Mac / Linux)
├── run_tests.bat         ← script de ejecución automática (Windows)
├── README.md             ← esta guía
│
├── scripts/
│   ├── generate_report.py   ← genera el reporte HTML profesional
│   └── parse_results.py     ← análisis QA detallado en terminal
│
└── reports/
    ├── OCM_RUN_SAMPLE_custom_report.html   ← ejemplo de reporte generado
    └── OCM_RUN_SAMPLE_results.json         ← ejemplo de resultados JSON
```

> 💡 Cada vez que corrés los tests, se crean nuevos archivos en la carpeta `reports/`
> con la fecha y hora del run. Los anteriores no se sobreescriben.

---

## PASO 1 — Obtener tu API key

La API key es necesaria para autenticarte con la API de Open Charge Map.
Es **gratuita** y se obtiene así:

1. Entrá a **https://openchargemap.org**
2. Hacé clic en **Sign In** (arriba a la derecha) y creá una cuenta, o iniciá sesión
3. Una vez dentro, hacé clic en tu nombre en la **barra de navegación superior**
4. Seleccioná **My Profile** en el menú desplegable
5. Dentro de tu perfil, navegá a la sección **My Apps**
6. Hacé clic en **Register An Application**
7. Poné cualquier nombre (ej: `Oppizi Test`) y guardá
8. Tu **API key** aparece en esa misma página — copiala

> ⚠️ No compartas tu API key ni la subas a repositorios públicos.

---

## OPCIÓN A — Correr los tests en Postman (visual)

Ideal para ver los resultados request por request con todos los detalles.

### Requisito
Tener **Postman** instalado → https://postman.com/downloads (gratis)

---

### 1. Importar los archivos

- Abrí Postman
- Hacé clic en **Import** (arriba a la izquierda)
- Seleccioná o arrastrá estos dos archivos:
  - `Oppizi – Open Charge Map API Tests.postman_collection.json`
  - `Oppizi – OCM API (Environment).postman_environment.json`
- Confirmá la importación

---

### 2. Configurar el entorno ⚠️ OBLIGATORIO

Sin este paso, todos los tests van a fallar porque no encuentran la API key.

- En la esquina **superior derecha** de Postman hay un selector que dice **"No Environment"**
- Hacé clic ahí y seleccioná **"Oppizi – OCM API (Environment)"**
- Hacé clic en el ícono del **ojo** 👁 al lado del selector
- Buscá la variable **`apiKey`**
- Hacé clic en el campo **Current Value** y pegá tu API key
- Cerrá el panel

---

### 3. Correr los tests

- En el panel izquierdo buscá la colección **"Oppizi – Open Charge Map API Tests"**
- Hacé clic derecho → **Run collection**
- En la ventana que se abre, hacé clic en **Run Oppizi – Open Charge Map API Tests**

---

### 4. Ver los resultados

Los resultados aparecen en Postman al terminar:

- ✅ **Verde** → el test pasó correctamente
- ❌ **Rojo** → el test falló (el error exacto aparece debajo)
- Hacé clic en cualquier test para ver el detalle completo de la request y la respuesta

---

## OPCIÓN B — Correr los tests desde la Terminal (automático)

Corre todos los tests de una sola vez y genera automáticamente un **reporte HTML profesional**.

---

### Requisitos previos

Verificá que tenés todo instalado abriendo la Terminal y corriendo estos comandos:

```bash
node --version
npm --version
newman --version
```

Si alguno devuelve `command not found`, seguí las instrucciones de instalación abajo.

---

### Instalación en Mac (si no tenés nada instalado)

Corré estos comandos **en orden**, uno por uno:

**1. Instalar Homebrew**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
> 💡 Va a pedir tu contraseña de Mac. Al escribirla **no se ve nada en pantalla** — ni asteriscos, ni puntos. Es normal. Escribila y presioná Enter igual.

**2. Instalar NVM** (administrador de versiones de Node)
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

**3. Recargar la terminal**
```bash
source ~/.zshrc
```

**4. Instalar Node.js**
```bash
nvm install --lts
nvm use --lts
```

**5. Verificar que quedó instalado**
```bash
node --version
npm --version
```
Los dos deben mostrar un número.

**6. Instalar Newman**
```bash
npm install -g newman newman-reporter-htmlextra
```

**7. Verificar Newman**
```bash
newman --version
```
Debe mostrar un número como `6.2.2`.

---

### Instalación en Windows (si no tenés nada instalado)

**1. Instalar Node.js**
- Entrá a https://nodejs.org
- Descargá el instalador con el botón verde **"LTS"**
- Ejecutá el instalador → siguiente, siguiente, instalar
- Reiniciá el símbolo del sistema después de instalar

**2. Instalar Newman**
```bat
npm install -g newman newman-reporter-htmlextra
```

---

### Correr los tests

**1. Abrí la Terminal** (Mac) o el **Símbolo del sistema** (Windows)

**2. Entrá a esta carpeta**
```bash
cd /ruta/a/Part 2 – API Testing + Automation
```
> 💡 **Truco Mac:** escribí `cd ` (con espacio) y arrastrá la carpeta desde el Finder
> a la Terminal. La ruta se completa sola. Presioná Enter.

**3. Dale permisos al script** (Mac — solo la primera vez)
```bash
chmod +x run_tests.sh
```

**4. Corré los tests**

En Mac / Linux:
```bash
OCM_API_KEY=TU_API_KEY_AQUI ./run_tests.sh
```

En Windows:
```bat
set OCM_API_KEY=TU_API_KEY_AQUI
run_tests.bat
```

> Reemplazá `TU_API_KEY_AQUI` con tu API key real del Paso 1.

---

### ¿Qué pasa mientras corren?

Vas a ver algo así en la terminal:

```
╔══════════════════════════════════════════════════════════════╗
║       OPPIZI – Open Charge Map API Test Automation          ║
╚══════════════════════════════════════════════════════════════╝

✓ API key configurada
✓ Newman: 6.2.2
✓ Colección: Oppizi – Open Charge Map API Tests.postman_collection.json
✓ Ambiente : Oppizi – OCM API (Environment).postman_environment.json

Run ID    : OCM_RUN_20260614_143022
Timestamp : 2026-06-14 14:30:22

▶  Ejecutando tests...

❏ POI – GET /poi/
↳ POI-01 – Status code is 200          ✓
↳ POI-02 – Response time under 1000ms  ✓
↳ POI-03 – Response is a JSON array    ✓
...

GENERANDO REPORTE...
✓ Reporte HTML generado
```

El proceso tarda aproximadamente **30–40 segundos**.

---

### ¿Qué se genera al terminar?

Se crean automáticamente dos archivos en la carpeta `reports/`:

| Archivo | Qué es | Cómo abrirlo |
|---|---|---|
| `OCM_RUN_..._custom_report.html` | Reporte visual completo | Se abre solo en el browser |
| `OCM_RUN_..._results.json` | Datos técnicos del run | Para compartir con el equipo |

El **reporte HTML se abre automáticamente** en tu browser al terminar. Contiene:

- 📊 **Scorecard** — pass rate, total de tests, passed, failed, duración
- ⚡ **Performance** — métricas P50, P90, P95, SLA
- 📋 **Tabla de resultados** — filtrable por Pass / Fail / POI / REF
- 🔍 **Análisis de fallos** — causa raíz de cada error con recomendaciones
- ⚠️ **Risk register** — riesgos identificados y action owners

Podés ver un ejemplo del reporte en `reports/OCM_RUN_SAMPLE_custom_report.html`.

---

## Tests incluidos

### GET /poi/ — 13 tests

| ID | Tipo | Qué valida |
|---|---|---|
| POI-01 | Status | Respuesta HTTP 200 |
| POI-02 | Performance | Tiempo de respuesta < 1000ms |
| POI-03 | Schema | Body es un array JSON |
| POI-04 | Schema | Cada POI tiene ID, UUID, AddressInfo y Connections |
| POI-05 | Schema | AddressInfo tiene Latitude, Longitude y CountryID |
| POI-06 | Schema | Connections tiene ID y ConnectionTypeID |
| POI-07 | Business logic | No devuelve más resultados que `maxresults` |
| POI-08 | Business logic | Todas las estaciones están dentro del radio de búsqueda |
| POI-09 | Business logic | El filtro por país funciona correctamente |
| POI-10 | Business logic | No hay IDs duplicados en la respuesta |
| POI-11 | Business logic | Todas las coordenadas son geográficamente válidas |
| POI-12 | Negativo | Sin API key el request es rechazado |
| POI-13 | Negativo | Coordenadas en el océano devuelven 0 resultados |

### GET /referencedata/ — 12 tests

| ID | Tipo | Qué valida |
|---|---|---|
| REF-01 | Status | Respuesta HTTP 200 |
| REF-02 | Performance | Tiempo de respuesta < 1000ms |
| REF-03 | Schema | Body es un objeto JSON |
| REF-04 | Schema | Tiene las 10 claves requeridas del catálogo |
| REF-05 | Schema | Todos los valores son arrays no vacíos |
| REF-06 | Schema | ConnectionTypes tiene ID y Title |
| REF-07 | Schema | Countries tiene ID e ISOCode |
| REF-08 | Business logic | No hay IDs duplicados en ninguna lista |
| REF-09 | Business logic | Todos los ISOCodes son strings de 2 caracteres |
| REF-10 | Business logic | Existe al menos un StatusType operacional |
| REF-11 | Business logic | Los ConnectionTypeIDs de POI existen en el catálogo |
| REF-12 | Negativo | Sin API key el request es rechazado |

---

## Variables de entorno

Podés cambiar estas variables en `Oppizi – OCM API (Environment).postman_environment.json`
para buscar estaciones en otra ciudad o con otros parámetros:

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `apiKey` | *(vacío — requerido)* | Tu API key de Open Charge Map |
| `lat` | `51.5074` | Latitud del centro de búsqueda (Londres) |
| `lng` | `-0.1278` | Longitud del centro de búsqueda (Londres) |
| `distance` | `10` | Radio de búsqueda en kilómetros |
| `maxresults` | `10` | Máximo de resultados por request |
| `countrycode` | `GB` | Código de país ISO (AR = Argentina, US = USA) |

---

## Troubleshooting

### ❌ `command not found: newman`
Newman no está instalado. Corré:
```bash
npm install -g newman newman-reporter-htmlextra
```

---

### ❌ `command not found: node` o `command not found: npm`
Node.js no está instalado. Seguí los pasos de instalación de arriba.

---

### ❌ `error: could not load environment` o `ENOENT: no such file or directory`

Dos causas posibles:

**Causa A — No estás en la carpeta correcta.**
Corré `ls` y verificá que ves los archivos `.json`. Si no, navegá hasta la carpeta correcta con `cd`.

**Causa B — Estás corriendo `newman` directamente en lugar del script.**
Usá siempre `./run_tests.sh` — el script detecta los archivos automáticamente sin importar cómo se llamen.

Si por alguna razón necesitás correr Newman directamente, los nombres de archivo tienen espacios y necesitan comillas:
```bash
newman run "Oppizi – Open Charge Map API Tests.postman_collection.json" \
  --environment "Oppizi – OCM API (Environment).postman_environment.json" \
  --env-var "apiKey=TU_API_KEY"
```

---

### ❌ Todos los tests fallan con `403 Forbidden`

Dos causas posibles:

**Causa A — API key incorrecta o vencida.**
Verificá que la key esté bien escrita y activa en:
https://openchargemap.org → My Profile → My Apps

**Causa B — Estás en una red corporativa o VPN.**
Algunas redes bloquean el dominio `api.openchargemap.io`.
Intentá con WiFi personal o datos móviles.

---

### ❌ `Permission denied: ./run_tests.sh`
El script no tiene permisos de ejecución. Corré:
```bash
chmod +x run_tests.sh
```

---

### ❌ La contraseña no aparece al escribirla en la terminal
Es comportamiento normal de Mac. Al escribir contraseñas **no se muestra nada en pantalla**
por seguridad. Escribí tu contraseña y presioná Enter aunque parezca que no pasa nada.

---

### ❌ `source ~/.zshrc` da error
Si tu Mac usa bash en lugar de zsh, probá:
```bash
source ~/.bash_profile
```
O simplemente cerrá y volvé a abrir la terminal.

---

### ❌ Los tests REF- son más lentos y algunos fallan por tiempo
El endpoint `/referencedata/` devuelve todo el catálogo de referencia y es más pesado
que `/poi/`. Es normal que tarde entre 1000ms y 1500ms. Si los fallos de performance
te molestan, podés ignorarlos — no afectan la funcionalidad real de la API.

---

### ❌ POI-12 y REF-12 siempre fallan esperando `401` pero reciben `403`
Es un comportamiento conocido del gateway de OCM: retorna `403` en lugar de `401`
para requests sin API key. No es un bug de los tests ni de la API en sí.
Está documentado en el Risk Register del reporte HTML.

---

*Oppizi QA Engineering — Part 2: API Testing + Automation*
*Open Charge Map API v3*
