import enum
import inspect
import logging
import subprocess
from logging.handlers import TimedRotatingFileHandler
from subprocess import Popen

import helix.utility.external
from helix.configuration import MANAGER_CFG
from helix.utility.external import External

logger = logging.getLogger(__name__)


class PrerequisiteIssueSeverity(enum.Enum):
    INFO = enum.auto()
    WARNING = enum.auto()
    ERROR = enum.auto()


class PrerequisiteIssueType(enum.Enum):
    CONFIG_ISSUE = enum.auto()
    MISSING_BINARY = enum.auto()
    BINARY_ERROR = enum.auto()


class PrerequisiteIssue:
    def __init__(
        self,
        severity: PrerequisiteIssueSeverity,
        type: PrerequisiteIssueType,
        description: str,
    ) -> None:
        self.severity = severity
        self.type = type
        self.description = description

    def __str__(self) -> str:
        return f"{self.severity.name}: {self.type.name}, {self.description}"

    def __repr__(self) -> str:
        return self.__str__()


class CheckPrerequisites:
    def __init__(self) -> None:
        self._repo = MANAGER_CFG.REPOSITORY
        self._ext = MANAGER_CFG.EXTERNAL
        self._gen = MANAGER_CFG.GENERAL
        self._config_logging()

    def _config_logging(self):
        if not self._repo.log_path.exists():
            self._repo.log_path.mkdir(parents=True, exist_ok=True)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            logger.removeHandler(handler)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        log_file = self._repo.log_path.joinpath("app.log")
        handler = TimedRotatingFileHandler(
            log_file, when="midnight", interval=1, backupCount=10
        )
        handler.suffix = "%Y-%m-%d"
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def check_prerequisites(self) -> list[PrerequisiteIssue]:
        # TODO: this sucks
        # TODO: empty config var should fallback on defaults with an INFO msg
        logger.info("Self test started.")
        old_level = logging.getLogger(helix.utility.external.__name__).level
        logging.getLogger(helix.utility.external.__name__).setLevel(logging.INFO)
        missing = {
            x: []
            for x in [
                PrerequisiteIssueSeverity.ERROR,
                PrerequisiteIssueSeverity.WARNING,
                PrerequisiteIssueSeverity.INFO,
            ]
        }
        if self._repo.metadata is None:
            missing[PrerequisiteIssueSeverity.ERROR].append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    "Metadata field is empty in repository config",
                )
            )
        elif not self._repo.metadata.exists():
            missing[PrerequisiteIssueSeverity.ERROR].append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    f"Metadata folder does not exist: {self._repo.metadata!s}",
                )
            )

        if self._repo.genomes is None:
            missing[PrerequisiteIssueSeverity.ERROR].append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    "Repository field is empty in repository config",
                )
            )
        elif not self._repo.genomes.exists():
            missing[PrerequisiteIssueSeverity.ERROR].append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    f"Repository folder does not exist: {self._repo.genomes!s}",
                )
            )

        if self._repo.temporary is None:
            missing[PrerequisiteIssueSeverity.ERROR].append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    "Temporary folder field is empty in repository config",
                )
            )
        elif not self._repo.temporary.exists():
            self._repo.temporary.mkdir(parents=True)
            missing[PrerequisiteIssueSeverity.INFO].append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.INFO,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    f"Temporary folder does not exist present. Creating: {self._repo.temporary!s}",
                )
            )

        if self._ext.root is None:
            missing[PrerequisiteIssueSeverity.ERROR].append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    f"Root folder does not exist: {self._ext.root!s}",
                )
            )
        elif not self._repo.temporary.exists():
            missing[PrerequisiteIssueSeverity.INFO].append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    f"Temp folder does not exist: {self._ext.root!s}. Creating",
                )
            )
            self._repo.temporary.mkdir(parents=True, exist_ok=True)

        if self._ext.threads is None:
            missing[PrerequisiteIssueSeverity.ERROR].append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    "Threads field is empty in external config",
                )
            )

        ext = External()
        members = inspect.getmembers(External, lambda x: inspect.isfunction(x))
        decorated = [x[1] for x in members if hasattr(x[1], "wrapper")]
        for f in decorated:
            try:
                result: Popen = f(
                    ext,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                result.communicate()
            except FileNotFoundError:
                m = PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.MISSING_BINARY,
                    f.__name__,
                )
                missing[PrerequisiteIssueSeverity.ERROR].append(m)
            except Exception as e:
                m = PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.BINARY_ERROR,
                    f"{f.__name__} : {e!s}",
                )
                missing[PrerequisiteIssueSeverity.ERROR].append(m)
        logging.getLogger(helix.utility.external.__name__).setLevel(old_level)
        logger.info(
            f"Self test ended: {len(missing[PrerequisiteIssueSeverity.ERROR])} errors, "
            + f"{len(missing[PrerequisiteIssueSeverity.WARNING])} warning, "
            + f"{len(missing[PrerequisiteIssueSeverity.INFO])} info."
        )
        return missing


if __name__ == "__main__":
    failing = CheckPrerequisites().check_prerequisites()
    if len(failing) == 0:
        print("All requirements are satisfied")
    else:
        for req in failing:
            print(req)
