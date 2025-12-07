from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from app.models import Dimensions, Operation, OperationType, Part, PartMetadata


DATA_FILE = Path("data/db.json")


def _ensure_storage():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps({"parts": []}))


def load_db() -> Dict[str, list]:
    _ensure_storage()
    return json.loads(DATA_FILE.read_text())


def save_db(data: Dict[str, list]):
    DATA_FILE.write_text(json.dumps(data, indent=2))


def list_parts() -> list[Part]:
    raw = load_db()["parts"]
    parts: list[Part] = []
    for item in raw:
        dims = Dimensions(**item["dimensions"])
        ops = [
            Operation(
                id=op.get("id"),
                type=OperationType(op["type"]),
                x=op["x"],
                y=op["y"],
                depth=op["depth"],
                diameter=op.get("diameter"),
                width=op.get("width"),
                height=op.get("height"),
                notes=op.get("notes"),
            )
            for op in item.get("operations", [])
        ]
        metadata = PartMetadata(**item.get("metadata", {}))
        parts.append(
            Part(
                id=item.get("id"),
                name=item["name"],
                dimensions=dims,
                operations=ops,
                metadata=metadata,
            )
        )
    return parts


def get_part(part_id: str) -> Part | None:
    for part in list_parts():
        if part.id == part_id:
            return part
    return None


def upsert_part(part: Part) -> Part:
    data = load_db()
    filtered = [item for item in data["parts"] if item["id"] != part.id]
    filtered.append(part.to_dict())
    data["parts"] = filtered
    save_db(data)
    return part
