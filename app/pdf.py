from __future__ import annotations

from datetime import datetime
from typing import List

from app.models import Operation, Part


PDF_TEMPLATE = """%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj
4 0 obj << /Length {length} >> stream
BT /F1 18 Tf 50 740 Td (Part: {name}) Tj ET
BT /F1 12 Tf 50 720 Td (Material: {material}) Tj ET
BT /F1 12 Tf 50 700 Td (Dimensions: {dims}) Tj ET
BT /F1 12 Tf 50 680 Td (Generated: {timestamp}) Tj ET
{operations}
endstream endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000074 00000 n 
0000000137 00000 n 
0000000230 00000 n 
0000000000 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
{startxref}
%%EOF"""


def render_operations(operations: List[Operation]) -> str:
    lines = []
    y = 660
    for op in operations:
        line = f"BT /F1 10 Tf 60 {y} Td (Op {op.id}: {op.type.value} @ {op.x},{op.y} depth {op.depth}) Tj ET"
        lines.append(line)
        y -= 16
    return "\n".join(lines)


def build_pdf(part: Part) -> bytes:
    ops_text = render_operations(part.operations)
    body = PDF_TEMPLATE.format(
        name=part.name,
        material=part.metadata.material or "N/A",
        dims=f"{part.dimensions.length} x {part.dimensions.width} x {part.dimensions.thickness} mm",
        timestamp=datetime.utcnow().isoformat(),
        operations=ops_text,
        length=400 + len(ops_text),
        startxref=400 + len(ops_text) + 120,
    )
    return body.encode("utf-8")
