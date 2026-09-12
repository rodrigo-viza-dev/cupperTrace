"""
CopperTrace - Dashboard web (Streamlit).
Capa de visualización sobre la cadena de custodia generada por app.py.
Datos simulados. Proyecto personal/académico.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pandas as pd
import streamlit as st

from app import (
    build_chain_and_events,
    generate_lots,
    validate_chain,
    tamper_block,
)

st.set_page_config(
    page_title="CopperTrace",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⛏️ CopperTrace")
st.caption(
    "Cadena de custodia para lotes de mineral con blockchain simplificado (SHA-256). "
    "Datos simulados. Inspirado en la adopción real de blockchain para trazabilidad "
    "y cumplimiento ESG en minería de cobre."
)

# ---------------------------------------------------------------------------
# Sidebar: parámetros
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Parámetros")
    n_lots = st.slider("Cantidad de lotes", min_value=5, max_value=200, value=25, step=5)
    seed = st.number_input("Semilla aleatoria", min_value=1, max_value=9999, value=42, step=1)

    st.divider()
    st.subheader("🧪 Simulación de manipulación")
    tamper_enabled = st.checkbox("Alterar un bloque retroactivamente", value=True)
    tamper_index = st.number_input(
        "Índice del bloque a alterar",
        min_value=1,
        max_value=max(1, n_lots * 3),
        value=5,
        step=1,
        disabled=not tamper_enabled,
    )

    run = st.button("🚀 Generar y validar", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Generación de datos
# ---------------------------------------------------------------------------
if "chain" not in st.session_state or run:
    lots = generate_lots(n_lots, seed=int(seed))
    chain, events = build_chain_and_events(lots)
    st.session_state["lots"] = lots
    st.session_state["chain"] = chain
    st.session_state["events"] = events

lots = st.session_state["lots"]
chain_clean = st.session_state["chain"]

# Cadena a mostrar: copia limpia, y si aplica, manipulación simulada
chain_display = copy.deepcopy(chain_clean)
if tamper_enabled:
    try:
        tamper_block(chain_display, int(tamper_index))
    except ValueError as e:
        st.warning(f"No se pudo manipular: {e}")

validation = pd.DataFrame(validate_chain(chain_display))
lots_df = pd.DataFrame(lots)

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
total = len(validation)
validos = int(validation["valid"].sum())
invalidos = total - validos
integridad = (validos / total * 100) if total else 0.0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Bloques", total)
c2.metric("Válidos", validos)
c3.metric("Inválidos", invalidos)
c4.metric("Integridad", f"{integridad:.1f}%")
c5.metric("Lotes", len(lots_df))

st.divider()

if invalidos == 0:
    st.success("✅ Cadena íntegra: todos los bloques son válidos.")
else:
    bloque_malo = validation[~validation["valid"]].iloc[0]
    st.error(
        f"🚨 Se detectaron **{invalidos}** bloque(s) comprometido(s). "
        f"Ejemplo → bloque **{int(bloque_malo['index'])}**, lote **{bloque_malo['lot_id']}**, "
        f"etapa **{bloque_malo['stage']}**: {bloque_malo['error']}"
    )

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_resumen, tab_cadena, tab_validacion, tab_lotes, tab_about = st.tabs(
    ["📊 Resumen", "🔗 Cadena", "🔍 Validación", "📦 Lotes", "ℹ️ Acerca de"]
)

with tab_resumen:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Tonelaje por tajo")
        by_pit = (
            lots_df.groupby("origin_pit")["tonnage"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(by_pit)

    with col_b:
        st.subheader("Ley promedio por tajo (%)")
        by_grade = (
            lots_df.groupby("origin_pit")["grade_pct"]
            .mean()
            .sort_values(ascending=False)
        )
        st.bar_chart(by_grade)

    st.subheader("Recuperación vs Ley")
    st.scatter_chart(
        lots_df,
        x="grade_pct",
        y="recovery_pct",
        color="origin_pit",
    )

with tab_cadena:
    st.subheader("Bloques de la cadena")
    chain_table = pd.DataFrame(
        [
            {
                "index": b.index,
                "timestamp": b.timestamp,
                "lot_id": b.lot_id,
                "stage": b.stage,
                "hash": b.hash[:20] + "…",
                "prev_hash": b.previous_hash[:20] + "…",
            }
            for b in chain_display
        ]
    )
    st.dataframe(chain_table, use_container_width=True, height=380)

    st.subheader("Línea de tiempo por lote")
    lot_options = sorted(lots_df["lot_id"].unique())
    selected_lot = st.selectbox("Selecciona un lote", lot_options)
    lot_blocks = [b for b in chain_display if b.lot_id == selected_lot]

    if lot_blocks:
        ev_df = pd.DataFrame(
            [
                {
                    "etapa": b.stage,
                    "timestamp": b.timestamp,
                    "hash": b.hash[:24] + "…",
                    "prev_hash": b.previous_hash[:24] + "…",
                }
                for b in lot_blocks
            ]
        )
        st.dataframe(ev_df, use_container_width=True)

with tab_validacion:
    st.subheader("Resultados de validación")
    invalidos_df = validation[~validation["valid"]]
    if len(invalidos_df) > 0:
        st.error(f"{len(invalidos_df)} bloque(s) inválido(s):")
        st.dataframe(invalidos_df, use_container_width=True)
    else:
        st.success("Todos los bloques son válidos.")

    st.subheader("Detalle completo")
    st.dataframe(validation, use_container_width=True, height=320)

    csv_bytes = validation.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar validación (CSV)",
        data=csv_bytes,
        file_name="block_validation.csv",
        mime="text/csv",
    )

with tab_lotes:
    st.subheader("Lotes de mineral")
    st.dataframe(lots_df, use_container_width=True, height=420)

    csv_lots = lots_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar lotes (CSV)",
        data=csv_lots,
        file_name="lots.csv",
        mime="text/csv",
    )

with tab_about:
    st.markdown(
        """
### ¿Qué es esto?

**CopperTrace** es una demo de cadena de custodia para lotes de mineral usando el
concepto central de blockchain: **una cadena de hashes SHA-256 enlazados**. Cada
etapa del lote (extracción → procesamiento → despacho) produce un bloque cuyo hash
depende del hash del bloque anterior. Si alguien altera un dato del pasado, todos
los hashes posteriores dejan de coincidir y la validación falla.

### ¿Qué NO es?

- No es una red descentralizada real.
- No usa Ethereum, Solidity ni contratos inteligentes.
- No usa datos reales: los lotes son simulados.

### ¿Por qué existe?

La industria del cobre está adoptando blockchain para trazabilidad y cumplimiento
ESG. La **Mesa de Trazabilidad de Emisiones de Alcance 3 de la Corporación Alta
Ley** reúne a Anglo American, Antofagasta Minerals, BHP, Codelco,
Freeport-McMoRan, Glencore, Lundin Mining y Teck. En Chile, Perú y Australia,
reguladores ya analizan marcos que reconozcan registros blockchain como
instrumentos válidos de auditoría de trazabilidad.

Este proyecto explora ese concepto desde una implementación mínima y verificable.
        """
    )

st.divider()
st.caption(
    "Proyecto personal/académico con datos simulados. "
)