import pytest
import tempfile
from pydre.rois import SpaceROI

def test_spaceroi_invalid_columns():
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w+", delete=False) as f:
        f.write("wrong,columns\\n1,2\\n")
        f.flush()
        with pytest.raises(ValueError):
            _ = SpaceROI(f.name)