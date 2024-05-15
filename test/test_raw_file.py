from pathlib import Path
from test.utility import MockFile
from unittest.mock import Mock, patch

from wgse.microarray.raw_file import RawEntry, RawFile


def test_raw_entry():
    sut = RawEntry("rs1", "1", 1, "AA")
    assert sut.template_entry == "rs1\t1\t1\n"

@patch('gzip.open')
@patch('pathlib.Path.open')
def test_compressed_raw_file(mock_open, mock_gzopen):
    lines = []
    file = Mock()
    file.write = lambda x: lines.append(x)
    
    mock_gzopen.side_effect = [MockFile(["#FOO", " rs1 \t 1 \t 1 \t AA \n", "rs2\tX\t123\tBB"])]
    mock_open.side_effect = [file]
    
    elements : list[RawEntry] = []
    
    for item in RawFile(Path("test.txt.gz")):
        elements.append(item)
        
    assert len(elements) == 2
    assert elements[0].id == "rs1"
    assert elements[0].chromosome == "1"
    assert elements[0].position == 1
    assert elements[0].result == "AA"
    assert elements[1].id == "rs2"
    assert elements[1].chromosome == "X"
    assert elements[1].position == 123
    assert elements[1].result == "BB"
    
# @patch('builtins.open')
# @patch('pathlib.Path.open')
# def test_compressed_raw_file(mock_open, mock_gzopen):
#     lines = []
#     file = Mock()
#     file.write = lambda x: lines.append(x)
    
#     mock_gzopen.side_effect = [MockFile(["#FOO", " rs1 \t 1 \t 1 \t AA \n", "rs2\tX\t123\tBB"])]
#     mock_open.side_effect = [file]
    
#     elements : list[RawEntry] = []
    
#     for item in RawFile(Path("test.txt")):
#         elements.append(item)
    
#     assert len(elements) == 2
#     assert elements[0].id == "rs1"
#     assert elements[0].chromosome == "1"
#     assert elements[0].position == 1
#     assert elements[0].result == "AA"
#     assert elements[1].id == "rs2"
#     assert elements[1].chromosome == "X"
#     assert elements[1].position == 123
#     assert elements[1].result == "BB"