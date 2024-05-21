<p align="center">
  <img src="https://avatars.githubusercontent.com/u/168782993?s=200&v=4">
</p>
  <h1 align="center">WGSE-NG</h1>

[![Documentation Status](https://readthedocs.org/projects/wgse-ng/badge/?version=latest)](https://wgse-ng.readthedocs.io/en/latest/?badge=latest)
[![Python application](https://github.com/WGSE-NG/WGSE-NG/actions/workflows/python-app.yml/badge.svg)](https://github.com/WGSE-NG/WGSE-NG/actions/workflows/python-app.yml/badge.svg)
[![Python Publish](https://github.com/WGSE-NG/WGSE-NG/actions/workflows/python-publish.yml/badge.svg)](https://github.com/WGSE-NG/WGSE-NG/actions/workflows/python-publish.yml/badge.svg)
[![Python Publish](https://github.com/WGSE-NG/WGSE-NG/actions/workflows/python-pyinstaller.yml/badge.svg)](https://github.com/WGSE-NG/WGSE-NG/actions/workflows/python-pyinstaller.yml/badge.svg)

This is my attempt to improve [WGSE](https://github.com/WGSExtract/WGSExtract-Dev). Still under heavy development. Don't expect anything working.

[PyPi Package](https://pypi.org/project/WGSE-NG/)

### Documentation
- [Read the docs](https://wgse-ng.readthedocs.io/en/latest/) (pretty much empty at this point)

### Launch
The only currently supported way to install `WGSE-NG` is with a pypi package.
This require python and pip installed. The procedure is the same on every supported OSs. Note WGSE-NG is still in alpha state and many things are not working or they may broke unexpectedly. A long term goal is get a [pyinstaller]() executable/installer for each supported platform. As of today, the GitHub action is there but it build a broken executable (and is for windows only).

```bash
sudo apt install libqt6waylandclient6 samtools bcftools -y # Only for Linux
python -m pip install wgse-ng
wgse
```

NOTE: on Windows all the executables needed beside WGSE-NG are shipped with another PyPI package upon which WGSE-NG depends. Installing through `pip` is hence sufficient to get `wgse-ng` working. On Linux `wgse-ng` expects all the executables to be available under `PATH`, consequentely there may be dependencies that need to be installed manually. The snippet above provide the dependencies list for Ubuntu, on other distro the command may change.

### Development
This section explain how to configure WGSE-NG for development.

_Note: The best experience for developing is with [VS Code](https://code.visualstudio.com/) as this project already contains sensible settings for VS code._

#### Windows
```bash
git clone https://github.com/WGSE-NG/WGSE-NG
cd WGSE-NG
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
wgse
```
#### Linux/WSL
```bash
sudo apt install libqt6waylandclient6 samtools bcftools -y
git clone https://github.com/WGSE-NG/WGSE-NG
cd WGSE-NG
python -m venv .venv
source ./.venv/bin/activate
python -m pip install -e .
wgse
```

#### pre-commit 
This repository uses [pre-commit](https://pre-commit.com/#intro) to ensure linting, formatting, and isort are executed before commit.
Its usage is optional but highly recommended. To install
```
python -m pip install pre-commit
pre-commit install
```

## Troubleshooting
- **pyside6-uic not found** when launching a debug from the IDE: you should restart the IDE. pyside6-uic executable (installed from a python dependency to compile .ui files into python modules) may not be found by the IDE if you just installed the dependency from a terminal inside the IDE it without restarting it first.
- **symbol lookup error** after launching WGSE from command line on Linux/WSL: likely your version of `libqt6waylandclient6` or one of its dependencies is too old and the python module for Qt is trying to fetch some symbols from it that were added in a subsequent version. You can try to run a `sudo apt update && sudo apt upgrade` but if that doesn't work unfortunately you need to upgrade the Qt version manually or use another distribution.

## What's working

- [x] Basic file info extraction
- [x] Index stats
- [x] Alignment stats
- [ ] Coverage stats
- [x] FASTA <-> SAM <-> BAM <-> CRAM conversion
- [ ] FASTQ <-> * conversion
- [x] Variant calling
- [x] Microarray converter(*)
- [x] Mitochondrial data extraction(*)
- [x] Y-DNA data extraction(*)
- [x] Reference genome identification (92 references supported)
- [ ] Installer
- [x] Crash stats
- [ ] Usage stats
- [X] Reference ingestion procedure
- [ ] Documentation

(*) Still needs to be wired to the GUI

## Supported references

### Add another reference
```python
manager = RepositoryManager()
manager.genomes.append(
    manager.ingest(
        "https://source/reference.fa",
        "NIH", # Anything that matches an entry in sources.json
        "38",  # Only 38 or 19
    )
)
GenomeMetadataLoader().save(manager.genomes)
```
