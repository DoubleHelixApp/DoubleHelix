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

## Documentation
- [Read the docs](https://wgse-ng.readthedocs.io/en/latest/) (pretty much empty at this point)

## Develop/Launch
_Note: The best experience for developing is with [VS Code](https://code.visualstudio.com/) as this project already contains sensible settings for VS code._
```bash
git clone https://github.com/chaplin89/WGSE-NG
cd WGSE-NG
python -m venv .venv
./.venv/Scripts/activate
python -m pip install -e .
python main.py
sudo apt install libegl1 libgl1 libxkbcommon0 libfontconfig1 -y
# If this is run from the terminal of an IDE, 
# at this point you should restart the IDE as
# there are some executables that are installed
# by pip that otherwise won't be found by the IDE.
```

## What's working

- [x] Basic file info extraction
- [x] Index stats
- [x] Alignment stats
- [ ] Coverage stats
- [ ] FASTQ <-> Aligned file conversion
- [x] SAM <-> BAM <-> CRAM conversion (WIP)
- [ ] Alignment
- [x] Variant calling (WIP)
- [x] Microarray converter
- [x] Mitochondrial data extraction (WIP)
- [x] Y-DNA data extraction (WIP)
- [x] Unaligned data extraction (WIP)
- [x] Reference genome identification (68 references supported)
- [ ] Installer
- [ ] Crash stats
- [ ] Usage stats
- [X] Reference ingestion procedure (partial)
- [ ] Documentation
