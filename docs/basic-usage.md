# Basic-usage

## Introduction
WGSE-NG is a tool designed for manipulating and extracting data from files representing whole-sequenced human genomes. It provides functionality to efficiently load, parse, filter, transform, and analyze genomic data. WGSE-NG is an attempt to re-engineering an existing tool called [WGSE](https://wgse.io). The name WGSE is an acronym that stands for "Whole Genome Sequencing Extract".

## OS support
WGSE runs on Windows, Linux, MacOS. Follow the installation procedure below according to your OS.

## Develop/Launch
_Note: The best experience is with [VS Code](https://code.visualstudio.com/) as this project already contains sensible settings for VS code._

```bash
git clone https://github.com/chaplin89/WGSE-NG
cd WGSE-NG
python -m venv .venv
./.venv/Scripts/activate
python -m pip install -r requirements.txt
python -m pip install -e .
python main.py
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
- [ ] SAM <-> BAM <-> CRAM conversion
- [ ] Alignment
- [ ] Variant calling
- [x] Microarray converter
- [ ] Mitochondrial data extraction
- [ ] Y-DNA data extraction
- [ ] Unaligned data extraction
- [x] Reference genome identification (68 references supported)
- [ ] Installer
- [ ] Crash stats
- [ ] Usage stats
- [X] Reference ingestion procedure (partial)
- [ ] Documentation

## Configuration

WGSE utilizes two configuration files to define its operational settings. These files provide a way to customize the software's behavior without modifying the code. The files are loaded in a specific order, allowing for overrides.

### File Priority

WGSE prioritizes configuration settings based on the order the files are loaded:

- **Global Configuration File** (configuration/main.ini): The first file loaded is located in a subdirectory of the WGSE path. This file is named wgse.ini by default. Settings defined here serve as the base configuration. This file is mostly useful when developing to have everything in the same folder.
- **Local Configuration File** (~/.wgse/main.ini): The second file loaded resides in the user's home directory within a folder named .wgse. Settings defined in this file can override the settings from the global configuration file.

### Configuration file sample

```ini
[general]
last_path = .

[external]
root = 3rd_party
threads = 24

[repository]
repository = repository
metadata = repository\metadata
temporary = repository\temp

[alignment_stats]
skip = 40000
samples = 20000
```
