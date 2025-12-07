from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_and_fetch_part():
    sample = (
        "NAME: Front panel\n"
        "MATERIAL: Oak\n"
        "DIM L=600 W=300 T=16\n"
        "OP TYPE=hole X=10 Y=20 DEPTH=16 DIAMETER=4\n"
    )

    response = client.post(
        "/api/parts/upload",
        files={"file": ("front.mpr", sample, "text/plain")},
    )
    assert response.status_code == 200
    part_id = response.json()["id"]

    part_response = client.get(f"/api/parts/{part_id}")
    assert part_response.status_code == 200
    assert part_response.json()["metadata"]["material"] == "Oak"

    operations = part_response.json()["operations"]
    operations[0]["diameter"] = 5

    update_response = client.put(f"/api/parts/{part_id}", json=operations)
    assert update_response.status_code == 200
    assert update_response.json()["operations"][0]["diameter"] == 5

    pdf_response = client.get(f"/api/parts/{part_id}/pdf/base64")
    assert pdf_response.status_code == 200
    assert "pdf" in pdf_response.json()
