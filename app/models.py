from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional
from uuid import uuid4


class OperationType(str, Enum):
    HOLE = "hole"
    POCKET = "pocket"
    GROOVE = "groove"


@dataclass
class Dimensions:
    length: float
    width: float
    thickness: float

    def __post_init__(self):
        for name, value in ("length", self.length), ("width", self.width), ("thickness", self.thickness):
            if value <= 0:
                raise ValueError(f"{name} must be positive")

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Operation:
    type: OperationType
    x: float
    y: float
    depth: float
    diameter: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    notes: Optional[str] = None
    id: str = field(default_factory=lambda: f"op-{uuid4().hex[:8]}")

    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = OperationType(self.type)
        if self.depth <= 0:
            raise ValueError("Depth must be positive")
        if self.type == OperationType.HOLE and not self.diameter:
            raise ValueError("Holes must include a diameter")
        if self.type in {OperationType.POCKET, OperationType.GROOVE}:
            if not self.width or not self.height:
                raise ValueError("Pocket and groove operations require width and height")

    def to_dict(self) -> dict:
        return asdict(self) | {"type": self.type.value}


@dataclass
class PartMetadata:
    material: Optional[str] = None
    description: Optional[str] = None
    source_file: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Part:
    name: str
    dimensions: Dimensions
    operations: List[Operation] = field(default_factory=list)
    metadata: PartMetadata = field(default_factory=PartMetadata)
    id: str = field(default_factory=lambda: f"part-{uuid4().hex[:8]}")

    def __post_init__(self):
        ids = {op.id for op in self.operations}
        if len(ids) != len(self.operations):
            raise ValueError("Operation IDs must be unique per part")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "dimensions": self.dimensions.to_dict(),
            "operations": [op.to_dict() for op in self.operations],
            "metadata": self.metadata.to_dict(),
        }
