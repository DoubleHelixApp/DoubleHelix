import filecmp
import shutil
from helix.data.genome import Genome
from helix.files.decompressor import Decompressor
from test.genome_fixtures import remote_repo_fixture, format_map


def test_decompress_gzip(remote_repo_fixture, tmp_path_factory):
    target = tmp_path_factory.mktemp("tmp") / format_map["gzip"]
    genome: Genome = remote_repo_fixture["gzip"]["genome"]
    shutil.copy(remote_repo_fixture["gzip"]["file_on_disk"], target)
    sut = Decompressor()
    output = sut.perform(genome, target)
    assert filecmp.cmp(output, remote_repo_fixture["fasta"]["file_on_disk"])
    assert remote_repo_fixture["fasta"]["md5"] == genome.decompressed_md5
    assert remote_repo_fixture["fasta"]["size"] == genome.decompressed_size


def test_decompress_fasta(remote_repo_fixture, tmp_path_factory):
    target = tmp_path_factory.mktemp("tmp") / format_map["fasta"]
    genome: Genome = remote_repo_fixture["fasta"]["genome"]
    shutil.copy(remote_repo_fixture["fasta"]["file_on_disk"], target)
    sut = Decompressor()
    output = sut.perform(genome, target)
    assert filecmp.cmp(output, remote_repo_fixture["fasta"]["file_on_disk"])
    assert remote_repo_fixture["fasta"]["md5"] == genome.decompressed_md5
    assert remote_repo_fixture["fasta"]["size"] == genome.decompressed_size


def test_decompress_bgzip(remote_repo_fixture, tmp_path_factory):
    target = tmp_path_factory.mktemp("tmp") / format_map["bgzip"]
    genome: Genome = remote_repo_fixture["bgzip"]["genome"]
    shutil.copy(remote_repo_fixture["bgzip"]["file_on_disk"], target)
    d = Decompressor()
    sut = d.perform(genome, target)

    # Testing the shortcut: should not touch a bgzip file
    assert filecmp.cmp(sut, remote_repo_fixture["bgzip"]["file_on_disk"])
    assert None == genome.decompressed_md5
    assert None == genome.decompressed_size


def test_decompress_zip(remote_repo_fixture, tmp_path_factory):
    target = tmp_path_factory.mktemp("tmp") / format_map["zip"]
    genome: Genome = remote_repo_fixture["zip"]["genome"]
    shutil.copy(remote_repo_fixture["zip"]["file_on_disk"], target)
    sut = Decompressor()
    output = sut.perform(genome, target)
    assert filecmp.cmp(output, remote_repo_fixture["fasta"]["file_on_disk"])
    assert remote_repo_fixture["fasta"]["md5"] == genome.decompressed_md5
    assert remote_repo_fixture["fasta"]["size"] == genome.decompressed_size


def test_decompress_razf(remote_repo_fixture, tmp_path_factory):
    target = tmp_path_factory.mktemp("tmp") / format_map["razf"]
    genome: Genome = remote_repo_fixture["razf"]["genome"]
    shutil.copy(remote_repo_fixture["razf"]["file_on_disk"], target)
    sut = Decompressor()
    output = sut.perform(genome, target)
    assert filecmp.cmp(output, remote_repo_fixture["fasta"]["file_on_disk"])
    assert remote_repo_fixture["fasta"]["md5"] == genome.decompressed_md5
    assert remote_repo_fixture["fasta"]["size"] == genome.decompressed_size
