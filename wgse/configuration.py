import configparser
import logging
import multiprocessing
from pathlib import Path

# Why third_party is not recognized by the IDE?
# See wgse/__init__.py
from wgse import third_party
from wgse import mtDNA
from wgse import metadata
import wgse

logger = logging.getLogger("configuration")
logging.getLogger().setLevel(logging.DEBUG)


class WGSEDefaults:
    """Specify some directory where to find configuration files."""

    WGSE_FOLDER = Path(__file__).parents[1]
    LOCAL_FOLDER = Path(Path.home(), ".wgse")
    LOCAL_CONFIG = Path(WGSE_FOLDER, "configuration", "main.ini")
    GLOBAL_CONFIG = Path(Path.home(), ".wgse", "main.ini")


class GeneralConfig:
    """General configuration for the app.

    Every attribute of this class can be loaded from the configuration
    files if present. See the documentation for ConfigurationManager.
    NOTE: you can add every type of variables as long as they can be
    constructed with a (single) string. Otherwise this will fail.

    Attributes:
        last_path (Path): path for the last file opened
        log_level (str): minimum log level. Possible values: DEBUG,
            INFO, WARNING, CRITICAL
    """

    def __init__(self) -> None:
        self.last_path: Path = Path.home()
        self.log_level: str = "DEBUG"


class ExternalConfig:
    """Configuration for 3rd party dependencies.

    Every attribute of this class can be loaded from the configuration
    files if present. See the documentation for ConfigurationManager.
    NOTE: you can add every type of variables as long as they can be
    constructed with a (single) string. Otherwise this will fail.

    Attributes:
        root (Path): folder that contains 3rd party dependencies.
            If this does not point to a valid directory, the files
            should be under PATH.
        threads (int): How many threads is possible to use.

    """

    def __init__(self) -> None:
        self.root: Path = Path(third_party.__file__).parent
        self.threads: int = multiprocessing.cpu_count()


class RepositoryConfig:
    """Configuration for reference genome and metadata repository.

    Every attribute of this class can be loaded from the configuration
    files if present. See the documentation for ConfigurationManager.
    NOTE: you can add every type of variables as long as they can be
    constructed with a (single) string. Otherwise this will fail.

    Attributes:
        repository (Path): Root folder for reference genomes.
        temporary (Path): Temporary files directory.
        metadata (Path): Root folder for metadata.
        mtdna (Path): Root folder for mtDNA files.
    """

    def __init__(self) -> None:
        self.genomes: Path = Path(WGSEDefaults.LOCAL_FOLDER, "genomes")
        self.temporary: Path = Path(WGSEDefaults.LOCAL_FOLDER, "temp")
        self.log_path: Path = Path(WGSEDefaults.LOCAL_FOLDER,"logs")
        self.metadata: Path = Path(metadata.__file__).parent
        self.mtdna: Path = Path(mtDNA.__file__).parent


class AlignmentStatsConfig:
    """Configuration for alignment stats calculation.

    Every attribute of this class can be loaded from the configuration
    files if present. See the documentation for ConfigurationManager.
    NOTE: you can add every type of variables as long as they can be
    constructed with a (single) string. Otherwise this will fail.

    Attributes:
        skip (int): How many samples to skip at the beginning
            of the file (where lots of repetitive and low quality
            sequences usually are).
        samples (int): How many samples to consider when calculating
            the stats.
    """

    def __init__(self) -> None:
        self.skip: int = 40000
        self.samples: int = 20000


class ConfigurationManager:
    """Initialize the configuration.

    Every static attribute declared here will be initialized
    when the class is initialized by looking for sections
    with the same as the attribute, containing the same attributes
    as the attribute.

    Attributes:
        GENERAL (GeneralConfig): Configuration parameters for the whole
            app.
        EXTERNAL (ExternalConfig): Configuration for 3rd party dependencies.
        REPOSITORY (RepositoryConfig): Configuration for reference genome
            and metadata repository.
        ALIGNMENT_STATS (AlignmentStatsConfig): Configuration for alignment
            stats calculation.
    """

    GENERAL: GeneralConfig = GeneralConfig()
    EXTERNAL: ExternalConfig = ExternalConfig()
    REPOSITORY: RepositoryConfig = RepositoryConfig()
    ALIGNMENT_STATS: AlignmentStatsConfig = AlignmentStatsConfig()

    def __init__(self) -> None:
        self.load()

    def load(self) -> None:
        self._parser = configparser.ConfigParser(interpolation=None)
        if WGSEDefaults.LOCAL_CONFIG.exists():
            logging.info(f"Loading {WGSEDefaults.LOCAL_CONFIG}")
        if WGSEDefaults.GLOBAL_CONFIG.exists():
            logging.info(f"Loading {WGSEDefaults.GLOBAL_CONFIG}")
        self._parser.read(WGSEDefaults.LOCAL_CONFIG)
        self._parser.read(WGSEDefaults.GLOBAL_CONFIG)

        for var_name, var_value in ConfigurationManager.__dict__.items():
            if var_name.startswith("__"):
                continue
            if getattr(var_value, "__dict__") == None:
                continue
            if type(var_value) == type(ConfigurationManager.load):
                continue

            section = var_name.lower()
            if section not in self._parser:
                continue
            for key, value in self._parser[section].items():
                if key not in var_value.__dict__:
                    logging.warning(f"Configuration {section}.{key} not known")
                    continue
                if value is None:
                    continue
                var_type = type(var_value.__dict__[key])
                var_value.__dict__[key] = var_type(value)

    def save(self, save_defaults=False):
        for var_name, var_value in ConfigurationManager.__dict__.items():
            if var_name.startswith("__"):
                continue
            if getattr(var_value, "__dict__") == None:
                continue
            if type(var_value) == type(ConfigurationManager.load):
                continue

            default_item = type(var_value)()
            section = var_name.lower()
            if section not in self._parser:
                self._parser.add_section(section)
            for key, value in var_value.__dict__.items():
                if default_item.__dict__[key] != value or save_defaults:
                    self._parser[section][key] = str(value)
            if len(self._parser[section]) == 0 and not save_defaults:
                self._parser.remove_section(section)
        ordered_config_paths = [WGSEDefaults.GLOBAL_CONFIG, WGSEDefaults.LOCAL_CONFIG]
        if not any([x.exists() for x in ordered_config_paths]):
            with ordered_config_paths[1].open("wt") as f:
                pass
        for config in ordered_config_paths:
            if not config.exists():
                continue
            with config.open("wt") as f:
                self._parser.write(f)
            break


MANAGER_CFG = None
if MANAGER_CFG is None:
    WGSEDefaults.GLOBAL_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    WGSEDefaults.GLOBAL_CONFIG.touch(exist_ok=True)
    MANAGER_CFG = ConfigurationManager()
    MANAGER_CFG.REPOSITORY.temporary.mkdir(parents=True, exist_ok=True)
    MANAGER_CFG.REPOSITORY.genomes.mkdir(parents=True, exist_ok=True)
    MANAGER_CFG.REPOSITORY.mtdna.mkdir(parents=True, exist_ok=True)
