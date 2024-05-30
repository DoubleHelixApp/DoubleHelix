# Basic-usage

## Introduction
WGSE-NG is a tool designed for manipulating and extracting data from files representing whole-sequenced human genomes. It provides functionality to efficiently load, parse, filter, transform, and analyze genomic data. WGSE-NG is an attempt to re-engineering an existing tool called [WGSE](https://wgse.io). The name WGSE is an acronym that stands for "Whole Genome Sequencing Extract".

## OS support
WGSE runs on Windows, Linux, MacOS. Follow the installation procedure below according to your OS.


### Launch
The only currently supported way to install `WGSE-NG` is with a pypi package.
This require python and pip installed. The procedure is the same on every supported OSs. Note WGSE-NG is still in alpha state and many things are not working or they may broke unexpectedly. There's a [pyinstaller](https://pyinstaller.org/en/stable/) build as well for Linux and Windows but is currently disabled. Will be enabled when the code will be more mature.

```bash
sudo apt install libqt6waylandclient6 samtools bcftools -y # Only for Linux
python -m pip install wgse-ng
wgse
```

_NOTE_: on Windows all the executables needed beside WGSE-NG are shipped with another PyPI package upon which WGSE-NG depends. Installing through `pip` is hence sufficient to get `wgse-ng` working. On Linux `wgse-ng` expects all the executables to be available under `PATH`, consequently there may be dependencies that need to be installed manually. The snippet above provide the dependencies list for Ubuntu, on other distro the command may change.

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

## FAQ

*How does it differs from the original WGSE?*
WGSE-NG is a re-engineering of WGSE with few improvements:
- A new GUI (based on pyqtside)
- An entirely re-written procedure to identify reference genomes
- It has a progress bar (not an easy task to implement one, see [here]() for the technical details)
-
- An HTML export of file information
