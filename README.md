# ⛏️ CopperTrace

**Cadena de custodia para lotes de mineral con blockchain simplificado.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cuppertrace-w6skmszvkv9va6urqglf3x.streamlit.app/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with Streamlit](https://img.shields.io/badge/Made%20with-Streamlit-FF4B4B.svg)](https://streamlit.io/)

🔗 **Demo en vivo:** https://cuppertrace-w6skmszvkv9va6urqglf3x.streamlit.app/

---

## 📌 ¿Qué es esto?

**CopperTrace** es una demo funcional de cómo un lote de mineral puede tener un
registro **inmutable y verificable** en cada etapa de su cadena de custodia
(extracción → procesamiento → despacho), usando el concepto central de
blockchain: **una cadena de hashes SHA-256 enlazados**.

Cada etapa del lote produce un bloque cuyo `hash` depende del hash del bloque
anterior. Si alguien altera un dato del pasado, todos los hashes posteriores
dejan de coincidir y el sistema detecta la manipulación señalando exactamente
en qué bloque ocurrió.

> **⚠️ Aviso honesto:** proyecto **personal/académico con datos simulados**.
> No participé en ningún hackathon ni competencia. No usa una red
> descentralizada real, ni Ethereum, ni contratos inteligentes. Está inspirado
> en la adopción real de blockchain para trazabilidad y cumplimiento ESG en la
> industria del cobre.

---

## 🎯 ¿Por qué existe?

Blockchain aplicado a trazabilidad minera no es una moda: es una tendencia
activa en la industria del cobre durante 2025–2026.

- La **Mesa de Trazabilidad de Emisiones de Alcance 3** de la **Corporación
  Alta Ley** reúne a ocho grandes mineras del cobre —Anglo American,
  Antofagasta Minerals, BHP, Codelco, Freeport-McMoRan, Glencore, Lundin
  Mining y Teck— trabajando en homologar medición y trazabilidad de emisiones
  en la cadena de valor.
- En Chile, Perú y Australia, reguladores ya analizan marcos normativos que
  reconozcan **registros blockchain como instrumentos válidos de auditoría**
  de trazabilidad.
- El mercado de soluciones blockchain aplicadas a ESG viene creciendo a doble
  dígito, con minería entre los sectores de mayor adopción para trazabilidad y
  reducción de opacidad en cadenas de suministro.

Este proyecto explora ese concepto desde una implementación mínima, honesta y
verificable, pensada como ejercicio de aprendizaje aplicado a un problema real
de la industria.

> **Nota:** las cifras y fuentes específicas deben verificarse contra los
> informes originales antes de citarse en contextos formales.

---

## ✨ Características

- 🔗 **Cadena de bloques real (simplificada):** cada bloque incluye
  `index`, `timestamp`, `lot_id`, `event_id`, `stage`, `payload`,
  `previous_hash` y `hash` (SHA-256).
- 🕵️ **Detección de manipulación:** si un dato del pasado se altera sin
  recalcular hashes, la validación falla y señala el bloque exacto.
- 🎲 **Generación reproducible:** dataset de lotes simulados con semilla
  configurable (tajo de origen, tonelaje, ley, tiempos, responsable de turno).
- 📊 **Dashboard web interactivo** (Streamlit): KPIs de integridad, línea de
  tiempo por lote, tabla de validación y simulación de manipulación con un
  clic.
- 💻 **CLI** para generar CSV exportables a Power BI / SQL.
- 🧩 **Esquema SQL** incluido para cargar los datos en PostgreSQL / SQL Server.

---

## 🖥️ Demo en vivo

👉 **https://cuppertrace-w6skmszvkv9va6urqglf3x.streamlit.app/**

Desde el navegador puedes:

1. Generar N lotes con semilla reproducible.
2. Ver la cadena completa de bloques con hashes enlazados.
3. **Simular una manipulación retroactiva** y ver cómo el sistema la detecta
   inmediatamente.
4. Descargar los CSV de lotes y validación.

---

## 🏗️ Cómo funciona

### 1. Generación de lotes simulados

Cada lote incluye: tajo de origen, tonelaje, ley (%), timestamps de
extracción/procesamiento/despacho, responsable de turno, planta, destino y
camión.

### 2. Construcción de la cadena

Por cada lote se generan **tres bloques** (uno por etapa). El hash de cada
bloque se calcula así:

```
hash = SHA256(index | timestamp | lot_id | event_id | stage | payload_json | previous_hash)
```

El `payload_json` se serializa de forma canónica (`sort_keys=True`,
`separators=(",", ":")`) para que el hash sea determinista.

### 3. Validación

Se recorre la cadena completa y se recalcula cada hash. Un bloque es válido
si:

- Su `previous_hash` coincide con el hash del bloque anterior.
- Su `hash` coincide con el hash recalculado a partir de sus datos actuales.

### 4. Detección de manipulación

Si alguien cambia un dato de un bloque del pasado (p. ej. el tonelaje
extraído) sin recalcular su hash, la validación falla y devuelve el bloque
exacto, el lote, la etapa y el motivo.

Ejemplo de salida del CLI:

```
Validación inicial: OK (76 bloques)
Validación tras manipular bloque 5: FALLÓ
  -> Bloque 5 | lote LOT-0002 | etapa procesamiento | hash inválido (datos alterados).
```

---

## 🧰 Stack técnico

| Capa | Tecnología |
|---|---|
| Lógica de cadena | Python 3.11+ (`hashlib`, `dataclasses`) |
| Dashboard web | Streamlit |
| Análisis de datos | pandas |
| Persistencia | CSV + esquema SQL (PostgreSQL / SQL Server) |
| BI opcional | Power BI (ver `sql/schema.sql`) |

---

## 🚀 Instalación y uso

### Requisitos

- Python 3.11 o superior
- pip
- (Opcional) WSL2 / Linux para desarrollo

### 1. Clonar el repo

```bash
git clone https://github.com/rodrigo-viza-dev/coppertrace.git
cd coppertrace
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate          # Linux / macOS / WSL
# .venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 3. Correr el dashboard web

```bash
streamlit run webapp.py
```

Se abre en `http://localhost:8501`.

### 4. (Opcional) Usar el CLI

```bash
python3 app.py --lots 25 --tamper-index 5
```

Parámetros:

| Flag | Descripción | Default |
|---|---|---|
| `--lots` | Cantidad de lotes simulados | `25` |
| `--tamper-index` | Bloque a manipular para la demo | `5` |
| `--output` | Carpeta de salida para CSV | `output` |

Genera:

```
output/
├── lots.csv
├── events.csv
├── blocks.csv
└── block_validation.csv
```

---

## 📁 Estructura del proyecto

```
coppertrace/
├── app.py                 # CLI + lógica de la cadena de custodia
├── webapp.py              # Dashboard interactivo en Streamlit
├── requirements.txt       # Dependencias Python
├── README.md
├── LICENSE
├── .gitignore
├── .gitattributes
├── sql/
│   └── schema.sql         # Esquema para PostgreSQL / SQL Server
└── output/                # CSV generados (no versionados)
```

---

## 🧪 Ejemplo de uso en Python

```python
from app import generate_lots, build_chain_and_events, validate_chain, tamper_block

# 1. Generar lotes simulados
lots = generate_lots(n=10, seed=42)

# 2. Construir la cadena de bloques
chain, events = build_chain_and_events(lots)

# 3. Validar
resultados = validate_chain(chain)
print(f"Bloques válidos: {sum(r['valid'] for r in resultados)} / {len(resultados)}")

# 4. Simular manipulación
tamper_block(chain, index=5)
resultados = validate_chain(chain)
for r in resultados:
    if not r["valid"]:
        print(f"Bloque {r['index']} comprometido: {r['error']}")
```

---

## 📊 Exportar a Power BI

Los CSV generados por el CLI están pensados para cargarse en Power BI. Ver
`sql/schema.sql` para las relaciones y medidas DAX sugeridas.

Tablas:
- `lots` — datos maestros del lote
- `events` — eventos individuales por etapa
- `blocks` — bloques de la cadena con hashes
- `block_validation` — resultado de la validación por bloque

Medidas sugeridas:

```dax
Integridad % =
DIVIDE(
    CALCULATE(COUNTROWS(block_validation), block_validation[valid] = TRUE()),
    COUNTROWS(block_validation),
    0
)

Tonelaje total = SUM(lots[tonnage])
Ley promedio % = AVERAGE(lots[grade_pct])
```

---

## 🗺️ Roadmap

- [ ] Tests unitarios con `pytest` para `validate_chain` y `tamper_block`.
- [ ] Dockerfile para correr con un solo `docker run`.
- [ ] GitHub Actions que corran los tests en cada push.
- [ ] Soporte para exportar a PostgreSQL directamente.
- [ ] Firma digital por responsable de turno (clave pública/privada simulada).
- [ ] Comparativa con Merkle Trees para agrupar lotes por turno.

---

## 🎓 Qué aprendí construyendo esto

- Cómo funciona **realmente** el concepto central de blockchain: no es "magia
  descentralizada", es una cadena de hashes enlazados donde la inmutabilidad
  emerge de la verificación matemática, no de la confianza en un servidor.
- Cómo diseñar **payloads canónicos** para que el hash sea determinista y
  reproducible entre runs.
- Cómo traducir una tendencia industrial real (trazabilidad ESG en minería)
  en un artefacto técnico verificable en lugar de quedarme en la teoría.
- Cómo desplegar una app de datos en **Streamlit Cloud** en menos de 10
  minutos.

---

## 🤝 Contribuciones

Este es un proyecto personal de aprendizaje, pero si encuentras un bug o
quieres proponer una mejora, abre un *issue* o manda un *pull request*.

---

## 📄 Licencia

MIT. Ver [LICENSE](LICENSE).

---

## 👤 Autor

**Rodrigo** — [@rodrigo-viza-dev](https://github.com/rodrigo-viza-dev)

Proyecto personal/académico. Datos simulados. Sin participación en
competencias ni hackathones.
