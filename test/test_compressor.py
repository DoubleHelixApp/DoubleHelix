import shutil

import pytest
from helix.data.genome import Genome
from helix.files.bgzip import BGzip
from helix.files.file_type_checker import FileType, FileTypeChecker
from test.genome_fixtures import format_map, remote_repo_fixture


def test_compress_gzip(remote_repo_fixture, tmp_path_factory):
    temp_folder = tmp_path_factory.mktemp("tmp") / format_map["gzip"]
    genome: Genome = remote_repo_fixture["gzip"]["genome"]
    local_repo_folder = tmp_path_factory.mktemp("genomes")
    genome.parent_folder = local_repo_folder
    shutil.copy(remote_repo_fixture["gzip"]["file_on_disk"], temp_folder)
    sut = BGzip()
    with pytest.raises(RuntimeError) as exc:
        output = sut.perform(genome, temp_folder)
    assert "not decompressed" in str(exc.value)


def test_compress_fasta(remote_repo_fixture, tmp_path_factory):
    target = tmp_path_factory.mktemp("tmp") / format_map["fasta"]
    genome: Genome = remote_repo_fixture["fasta"]["genome"]
    local_repo_folder = tmp_path_factory.mktemp("genomes")
    genome.parent_folder = local_repo_folder
    shutil.copy(remote_repo_fixture["fasta"]["file_on_disk"], target)
    sut = BGzip()
    output = sut.perform(genome, target)
    assert FileTypeChecker().get_type(output) == FileType.BGZIP
    assert genome.gzi.exists()


def test_compress_bgzip(remote_repo_fixture, tmp_path_factory):
    target = tmp_path_factory.mktemp("tmp") / format_map["bgzip"]
    genome: Genome = remote_repo_fixture["bgzip"]["genome"]
    local_repo_folder = tmp_path_factory.mktemp("genomes")
    genome.parent_folder = local_repo_folder
    shutil.copy(remote_repo_fixture["bgzip"]["file_on_disk"], target)
    sut = BGzip()
    output = sut.perform(genome, target)
    assert FileTypeChecker().get_type(output) == FileType.BGZIP
    assert genome.gzi.exists()


def test_compress_zip(remote_repo_fixture, tmp_path_factory):
    target = tmp_path_factory.mktemp("tmp") / format_map["zip"]
    genome: Genome = remote_repo_fixture["zip"]["genome"]
    local_repo_folder = tmp_path_factory.mktemp("genomes")
    genome.parent_folder = local_repo_folder
    shutil.copy(remote_repo_fixture["zip"]["file_on_disk"], target)
    sut = BGzip()
    with pytest.raises(RuntimeError) as exc:
        sut.perform(genome, target)
    assert "not decompressed" in str(exc.value)


def test_compress_razf(remote_repo_fixture, tmp_path_factory):
    target = tmp_path_factory.mktemp("tmp") / format_map["razf"]
    genome: Genome = remote_repo_fixture["razf"]["genome"]
    local_repo_folder = tmp_path_factory.mktemp("genomes")
    genome.parent_folder = local_repo_folder
    shutil.copy(remote_repo_fixture["razf"]["file_on_disk"], target)
    sut = BGzip()
    with pytest.raises(RuntimeError) as exc:
        sut.perform(genome, target)
    assert "not decompressed" in str(exc.value)
