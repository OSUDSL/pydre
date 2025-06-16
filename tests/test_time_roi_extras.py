import pytest
from pydre.rois import TimeROI

def test_parse_timestamp_invalid_format():
    with pytest.raises(ValueError):
        TimeROI.parseTimeStamp("invalid_format")