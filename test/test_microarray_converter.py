from test.test_fasta import MockPath

import pytest

from helix.configuration import RepositoryConfig
from helix.microarray.microarray_converter import MicroarrayConverter

# def test_every_target_has_formatter():
#     assert all(x in TARGET_FORMATTER_MAP for x in MicroarrayConverterTarget)


def test_inexistent_head_folder_raise():
    config = RepositoryConfig()
    config.metadata = MockPath(exists=False)
    microarray_templates = MockPath(exists=False, name="microarray_templates")
    microarray_templates.joinpath = lambda x: MockPath(
        [], False if x == "body" else True, x
    )
    config.metadata.joinpath = lambda _: microarray_templates
    with pytest.raises(FileNotFoundError) as e:
        MicroarrayConverter(config)
    assert "template body"


def test_inexistent_head_folder_raise():
    config = RepositoryConfig()
    config.metadata = MockPath(exists=False)
    microarray_templates = MockPath(exists=False, name="microarray_templates")
    microarray_templates.joinpath = lambda x: MockPath(
        [], False if x == "head" else True, x
    )
    config.metadata.joinpath = lambda _: microarray_templates
    with pytest.raises(FileNotFoundError) as e:
        MicroarrayConverter(config)
    assert "template head"


def test_inexistent_head_folder_raise():
    config = RepositoryConfig()
    config.metadata = MockPath(exists=False)
    microarray_templates = MockPath("microarray_templates", exists=False)
    microarray_templates.joinpath = lambda x: MockPath(
        x,
        buffer=[],
        exists=False if x == "body" else True,
    )
    config.metadata.joinpath = lambda _: microarray_templates
    with pytest.raises(FileNotFoundError) as e:
        MicroarrayConverter(config)
    assert "template body"


# @patch('pathlib.Path.exists')
# @patch('pathlib.Path.open')
# @patch('gzip.open')
# @patch('shutil.copy')
# def test_missing_path(mock_copy, mock_gzip_open, mock_open, mock_exists):
#     output_lines = []
#     template_body = MockFile(["rs1\t1\t1"])
#     input_file = MockFile(["rs1\t1\t1\tAA"])
#     output_file = MockFile([])
#     output_file.write = lambda x: output_lines.append(x)

#     mock_open.side_effect = [input_file, output_file]
#     mock_exists.side_effect = [True, True, True, True]
#     mock_gzip_open.side_effect = [template_body]

#     config = RepositoryConfig()
#     config.metadata = Path("blah")
#     sut = MicroarrayConverter(config)
#     sut.convert(Path("foo"), MicroarrayConverterTarget.Ancestry_v1)
#     pass
