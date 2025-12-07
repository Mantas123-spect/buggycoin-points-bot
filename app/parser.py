from __future__ import annotations

from typing import Iterable, List

from app.models import Dimensions, Operation, OperationType, Part, PartMetadata


def parse_key_value(line: str):
    if ":" in line:
        key, value = line.split(":", 1)
    elif "=" in line:
        key, value = line.split("=", 1)
    else:
        return None, None
    return key.strip().lower(), value.strip()


def parse_operation(tokens: Iterable[str]) -> Operation:
    data = {}
    for token in tokens:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        data[key.lower()] = value

    op_type = OperationType(data.get("type", "hole"))
    x = float(data.get("x", 0))
    y = float(data.get("y", 0))
    depth = float(data.get("depth", data.get("z", 0)))

    base_kwargs = {
        "type": op_type,
        "x": x,
        "y": y,
        "depth": depth,
        "notes": data.get("notes"),
    }

    if op_type == OperationType.HOLE:
        base_kwargs["diameter"] = float(data.get("diameter", data.get("dia", 0)))
    else:
        base_kwargs["width"] = float(data.get("width", data.get("w", 0)))
        base_kwargs["height"] = float(data.get("height", data.get("h", 0)))

    return Operation(**base_kwargs)


def parse_mpr(content: str, file_name: str | None = None) -> Part:
    name = file_name or "untitled"
    lines = [line.strip() for line in content.splitlines() if line.strip()]

    meta = PartMetadata(source_file=file_name)
    dims = Dimensions(length=1, width=1, thickness=1)
    operations: List[Operation] = []

    for line in lines:
        lower = line.lower()
        if lower.startswith("dim"):
            _, raw = lower.split(maxsplit=1)
            kv = dict(token.split("=") for token in raw.split())
            dims = Dimensions(
                length=float(kv.get("l", kv.get("length", 0))),
                width=float(kv.get("w", kv.get("width", 0))),
                thickness=float(kv.get("t", kv.get("thickness", 0))),
            )
        elif lower.startswith("operation") or lower.startswith("op"):
            tokens = line.split()[1:]
            operations.append(parse_operation(tokens))
        else:
            key, value = parse_key_value(line)
            if key == "name" and not file_name:
                name = value
            elif key == "material":
                meta.material = value
            elif key == "description":
                meta.description = value

    return Part(name=name, dimensions=dims, operations=operations, metadata=meta)
