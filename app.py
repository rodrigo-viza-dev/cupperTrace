"""
CopperTrace - Cadena de custodia para lotes de mineral.
Blockchain simplificado: cadena de hashes SHA-256 enlazados.
Datos simulados. Proyecto personal/académico.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

GENESIS_PREVIOUS_HASH = "0" * 64


@dataclass
class Block:
    index: int
    timestamp: str
    lot_id: str
    event_id: str
    stage: str
    payload: dict[str, Any]
    previous_hash: str
    hash: str


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def compute_hash(
    index: int,
    timestamp: str,
    lot_id: str,
    event_id: str,
    stage: str,
    payload_json: str,
    previous_hash: str,
) -> str:
    raw = f"{index}|{timestamp}|{lot_id}|{event_id}|{stage}|{payload_json}|{previous_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def create_genesis_block() -> Block:
    timestamp = "2025-01-01T00:00:00"
    payload = {"message": "Genesis Block - CopperTrace"}
    event_id = "GENESIS"
    stage = "GENESIS"
    lot_id = "GENESIS"
    payload_json = canonical_json(payload)
    h = compute_hash(0, timestamp, lot_id, event_id, stage, payload_json, GENESIS_PREVIOUS_HASH)
    return Block(0, timestamp, lot_id, event_id, stage, payload, GENESIS_PREVIOUS_HASH, h)


def append_block(
    chain: list[Block],
    lot_id: str,
    event_id: str,
    stage: str,
    payload: dict[str, Any],
    timestamp: str,
) -> Block:
    index = len(chain)
    previous_hash = chain[-1].hash
    payload_json = canonical_json(payload)
    h = compute_hash(index, timestamp, lot_id, event_id, stage, payload_json, previous_hash)
    block = Block(index, timestamp, lot_id, event_id, stage, payload, previous_hash, h)
    chain.append(block)
    return block


def validate_chain(chain: list[Block]) -> list[dict[str, Any]]:
    results = []
    for i, block in enumerate(chain):
        expected_prev = GENESIS_PREVIOUS_HASH if i == 0 else chain[i - 1].hash
        prev_ok = block.previous_hash == expected_prev

        payload_json = canonical_json(block.payload)
        expected_hash = compute_hash(
            block.index,
            block.timestamp,
            block.lot_id,
            block.event_id,
            block.stage,
            payload_json,
            block.previous_hash,
        )
        hash_ok = block.hash == expected_hash
        valid = prev_ok and hash_ok

        error = ""
        if not prev_ok:
            error += "previous_hash no coincide. "
        if not hash_ok:
            error += "hash inválido (datos alterados). "

        results.append({
            "index": block.index,
            "lot_id": block.lot_id,
            "event_id": block.event_id,
            "stage": block.stage,
            "previous_hash_ok": prev_ok,
            "hash_ok": hash_ok,
            "valid": valid,
            "error": error.strip(),
        })
    return results


def tamper_block(chain: list[Block], index: int) -> None:
    """Modifica un dato de un bloque sin actualizar su hash. Simula manipulación retroactiva."""
    if index <= 0 or index >= len(chain):
        raise ValueError("Índice de bloque a manipular fuera de rango.")

    block = chain[index]
    if "tonnage" in block.payload:
        block.payload["tonnage"] = round(float(block.payload["tonnage"]) + 1000.0, 2)
    elif "recovered_tonnage" in block.payload:
        block.payload["recovered_tonnage"] = round(float(block.payload["recovered_tonnage"]) + 1000.0, 2)
    elif "dispatch_tonnage" in block.payload:
        block.payload["dispatch_tonnage"] = round(float(block.payload["dispatch_tonnage"]) + 1000.0, 2)
    else:
        block.payload["tampered"] = True


def generate_lots(n: int, seed: int = 42) -> list[dict[str, Any]]:
    random.seed(seed)
    pits = ["Tajo Norte", "Tajo Sur", "Tajo Este", "Tajo Oeste"]
    plants = ["Planta Concentradora 1", "Planta Concentradora 2"]
    destinations = ["Puerto Matarani", "Puerto Callao", "Fundición Local"]
    shifts = ["A", "B", "C", "D"]
    base = datetime(2025, 1, 1, 6, 0, 0)
    lots = []

    for i in range(1, n + 1):
        lot_id = f"LOT-{i:04d}"
        origin_pit = random.choice(pits)
        tonnage = round(random.uniform(800, 2500), 2)
        grade_pct = round(random.uniform(0.35, 1.20), 3)

        extraction_ts = base + timedelta(days=random.randint(0, 30), hours=random.randint(0, 12))
        processing_ts = extraction_ts + timedelta(hours=random.randint(2, 10))
        dispatch_ts = processing_ts + timedelta(hours=random.randint(4, 24))

        shift_lead = f"Supervisor-{random.choice(shifts)}{random.randint(1, 4)}"
        plant = random.choice(plants)
        destination = random.choice(destinations)
        truck_id = f"TRK-{random.randint(100, 999)}"

        recovered_tonnage = round(tonnage * random.uniform(0.85, 0.95), 2)
        recovery_pct = round((recovered_tonnage / tonnage) * 100, 2)
        dispatch_tonnage = round(recovered_tonnage * random.uniform(0.95, 1.0), 2)

        lots.append({
            "lot_id": lot_id,
            "origin_pit": origin_pit,
            "tonnage": tonnage,
            "grade_pct": grade_pct,
            "extraction_ts": extraction_ts.isoformat(timespec="seconds"),
            "processing_ts": processing_ts.isoformat(timespec="seconds"),
            "dispatch_ts": dispatch_ts.isoformat(timespec="seconds"),
            "shift_lead": shift_lead,
            "plant": plant,
            "destination": destination,
            "truck_id": truck_id,
            "recovered_tonnage": recovered_tonnage,
            "recovery_pct": recovery_pct,
            "dispatch_tonnage": dispatch_tonnage,
        })
    return lots


def build_chain_and_events(lots: list[dict[str, Any]]) -> tuple[list[Block], list[dict[str, Any]]]:
    chain = [create_genesis_block()]
    events = []

    for lot in lots:
        # Extracción
        event_id = f"EVT-{lot['lot_id']}-EXT"
        payload = {
            "event_id": event_id,
            "lot_id": lot["lot_id"],
            "stage": "extraccion",
            "origin_pit": lot["origin_pit"],
            "tonnage": lot["tonnage"],
            "grade_pct": lot["grade_pct"],
            "responsible": lot["shift_lead"],
        }
        append_block(chain, lot["lot_id"], event_id, "extraccion", payload, lot["extraction_ts"])
        events.append({
            "event_id": event_id,
            "lot_id": lot["lot_id"],
            "stage": "extraccion",
            "timestamp": lot["extraction_ts"],
            "responsible": lot["shift_lead"],
            "details_json": canonical_json(payload),
        })

        # Procesamiento
        event_id = f"EVT-{lot['lot_id']}-PRO"
        payload = {
            "event_id": event_id,
            "lot_id": lot["lot_id"],
            "stage": "procesamiento",
            "plant": lot["plant"],
            "recovered_tonnage": lot["recovered_tonnage"],
            "recovery_pct": lot["recovery_pct"],
            "responsible": lot["shift_lead"],
        }
        append_block(chain, lot["lot_id"], event_id, "procesamiento", payload, lot["processing_ts"])
        events.append({
            "event_id": event_id,
            "lot_id": lot["lot_id"],
            "stage": "procesamiento",
            "timestamp": lot["processing_ts"],
            "responsible": lot["shift_lead"],
            "details_json": canonical_json(payload),
        })

        # Despacho
        event_id = f"EVT-{lot['lot_id']}-DES"
        payload = {
            "event_id": event_id,
            "lot_id": lot["lot_id"],
            "stage": "despacho",
            "destination": lot["destination"],
            "truck_id": lot["truck_id"],
            "dispatch_tonnage": lot["dispatch_tonnage"],
            "responsible": lot["shift_lead"],
        }
        append_block(chain, lot["lot_id"], event_id, "despacho", payload, lot["dispatch_ts"])
        events.append({
            "event_id": event_id,
            "lot_id": lot["lot_id"],
            "stage": "despacho",
            "timestamp": lot["dispatch_ts"],
            "responsible": lot["shift_lead"],
            "details_json": canonical_json(payload),
        })

    return chain, events


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def export_outputs(
    output_dir: Path,
    lots: list[dict[str, Any]],
    events: list[dict[str, Any]],
    chain: list[Block],
    validation: list[dict[str, Any]],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    lots_fields = [
        "lot_id", "origin_pit", "tonnage", "grade_pct", "extraction_ts", "processing_ts",
        "dispatch_ts", "shift_lead", "plant", "destination", "truck_id",
        "recovered_tonnage", "recovery_pct", "dispatch_tonnage",
    ]
    write_csv(output_dir / "lots.csv", lots, lots_fields)

    events_fields = ["event_id", "lot_id", "stage", "timestamp", "responsible", "details_json"]
    write_csv(output_dir / "events.csv", events, events_fields)

    blocks_rows = []
    for b in chain:
        blocks_rows.append({
            "index": b.index,
            "timestamp": b.timestamp,
            "lot_id": b.lot_id,
            "event_id": b.event_id,
            "stage": b.stage,
            "previous_hash": b.previous_hash,
            "hash": b.hash,
            "payload_json": canonical_json(b.payload),
        })
    blocks_fields = ["index", "timestamp", "lot_id", "event_id", "stage", "previous_hash", "hash", "payload_json"]
    write_csv(output_dir / "blocks.csv", blocks_rows, blocks_fields)

    validation_fields = [
        "index", "lot_id", "event_id", "stage",
        "previous_hash_ok", "hash_ok", "valid", "error",
    ]
    write_csv(output_dir / "block_validation.csv", validation, validation_fields)


def main() -> None:
    parser = argparse.ArgumentParser(description="CopperTrace - Cadena de custodia para lotes de mineral")
    parser.add_argument("--lots", type=int, default=25, help="Cantidad de lotes simulados")
    parser.add_argument("--tamper-index", type=int, default=5, help="Índice de bloque a manipular para demo")
    parser.add_argument("--output", type=str, default="output", help="Directorio de salida")
    args = parser.parse_args()

    lots = generate_lots(args.lots)
    chain, events = build_chain_and_events(lots)

    validation_ok = validate_chain(chain)
    all_ok = all(r["valid"] for r in validation_ok)
    print(f"Validación inicial: {'OK' if all_ok else 'FALLÓ'} ({len(chain)} bloques)")

    export_outputs(Path(args.output), lots, events, chain, validation_ok)

    try:
        tamper_block(chain, args.tamper_index)
        validation_tampered = validate_chain(chain)
        all_ok_tampered = all(r["valid"] for r in validation_tampered)
        print(f"Validación tras manipular bloque {args.tamper_index}: {'OK' if all_ok_tampered else 'FALLÓ'}")
        for r in validation_tampered:
            if not r["valid"]:
                print(f"  -> Bloque {r['index']} | lote {r['lot_id']} | etapa {r['stage']} | {r['error']}")
        export_outputs(Path(args.output) / "tampered", lots, events, chain, validation_tampered)
    except ValueError as e:
        print(f"No se pudo manipular el bloque: {e}")

    print(f"Archivos generados en: {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()