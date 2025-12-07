from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.db import get_part, list_parts, upsert_part
from app.models import Operation, Part, PartMetadata
from app.pdf import build_pdf
from app.parser import parse_mpr

app = FastAPI(title="WoodWOP Parser API", version="0.1.0")

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/api/parts/upload", response_model=Part)
async def upload_part(file: UploadFile = File(...)):
    if not file.filename.endswith(".mpr"):
        raise HTTPException(status_code=400, detail="Only .mpr files are supported")

    content = (await file.read()).decode("utf-8")
    part = parse_mpr(content, file.filename)
    part.metadata.source_file = file.filename

    dest = UPLOAD_DIR / file.filename
    dest.write_text(content)

    upsert_part(part)
    return JSONResponse(part.to_dict())


@app.get("/api/parts", response_model=List[Part])
async def fetch_parts():
    return JSONResponse([part.to_dict() for part in list_parts()])


@app.get("/api/parts/{part_id}", response_model=Part)
async def fetch_part(part_id: str):
    part = get_part(part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return JSONResponse(part.to_dict())


@app.put("/api/parts/{part_id}", response_model=Part)
async def update_part(part_id: str, operations: List[Operation]):
    part = get_part(part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    normalized = []
    for op in operations:
        if isinstance(op, Operation):
            normalized.append(op)
        else:
            normalized.append(Operation(**op))
    part.operations = normalized
    upsert_part(part)
    return JSONResponse(part.to_dict())


@app.post("/api/parts/{part_id}/metadata", response_model=Part)
async def update_metadata(part_id: str, metadata: PartMetadata):
    part = get_part(part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    part.metadata = metadata if isinstance(metadata, PartMetadata) else PartMetadata(**metadata)
    upsert_part(part)
    return JSONResponse(part.to_dict())


@app.get("/api/parts/{part_id}/pdf")
async def generate_pdf(part_id: str):
    part = get_part(part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    pdf_bytes = build_pdf(part)
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf")


@app.get("/api/parts/{part_id}/pdf/base64")
async def generate_pdf_base64(part_id: str):
    part = get_part(part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    pdf_bytes = build_pdf(part)
    encoded = base64.b64encode(pdf_bytes).decode("ascii")
    return JSONResponse({"pdf": encoded})
