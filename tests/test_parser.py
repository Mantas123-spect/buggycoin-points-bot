import pytest

from app.models import OperationType
from app.parser import parse_mpr


SAMPLE_MPR = """
NAME: Panel A
MATERIAL: Birch
DESCRIPTION: Sample panel
DIM L=800 W=400 T=18
OP TYPE=hole X=50 Y=60 DEPTH=18 DIAMETER=5 NOTES=Shelf peg
OPERATION TYPE=pocket X=120 Y=100 DEPTH=6 WIDTH=30 HEIGHT=50
OP TYPE=groove X=300 Y=200 DEPTH=4 WIDTH=6 HEIGHT=18
"""


def test_parse_mpr_parses_dimensions_and_operations():
    part = parse_mpr(SAMPLE_MPR, "panel.mpr")

    assert part.name == "panel.mpr"
    assert part.metadata.material == "Birch"
    assert part.dimensions.length == 800
    assert part.dimensions.width == 400
    assert part.dimensions.thickness == 18
    assert len(part.operations) == 3

    hole, pocket, groove = part.operations
    assert hole.type is OperationType.HOLE
    assert hole.diameter == 5
    assert pocket.type is OperationType.POCKET
    assert pocket.width == 30
    assert groove.type is OperationType.GROOVE
    assert groove.height == 18
