import enum
import inspect
import logging
import subprocess
import wgse.utility.external
from subprocess import Popen

from wgse.configuration import MANAGER_CFG
from wgse.utility.external import External

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
        self.failed = self.check_prerequisites()

    def check_prerequisites(self) -> list[PrerequisiteIssue]:
        # TODO: this sucks
        # TODO: empty config var should fallback on defaults with an INFO msg
        old_level = logging.getLogger(wgse.utility.external.__name__).level
        logging.getLogger(wgse.utility.external.__name__).setLevel(logging.INFO)
        missing = []
        if self._repo.metadata is None:
            missing.append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    "Metadata field is empty in repository config",
                )
            )
        elif not self._repo.metadata.exists():
            missing.append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    f"Metadata folder does not exist: {self._repo.metadata!s}",
                )
            )

        if self._repo.genomes is None:
            missing.append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    "Repository field is empty in repository config",
                )
            )
        elif not self._repo.genomes.exists():
            missing.append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    f"Repository folder does not exist: {self._repo.genomes!s}",
                )
            )

        if self._repo.temporary is None:
            missing.append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    "Temporary folder field is empty in repository config",
                )
            )
        elif not self._repo.temporary.exists():
            self._repo.temporary.mkdir(parents=True)
            missing.append(
                PrerequisiteIssue(
                    PrerequisiteIssueSeverity.INFO,
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    f"Temporary folder does not exist present. Creating: {self._repo.temporary!s}",
                )
            )

        if self._ext.root is None:
            missing.append("Root folder field is empty in external config")
        elif not self._repo.temporary.exists():
            missing.append(
                PrerequisiteIssue(
                    PrerequisiteIssueType.CONFIG_ISSUE,
                    f"Root folder does not exist: {self._ext.root!s}",
                )
            )

        if self._ext.threads is None:
            missing.append(
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
            except FileNotFoundError as e:
                m = PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.MISSING_BINARY,
                    f.__name__,
                )
                missing.append(m)
            except Exception as e:
                m = PrerequisiteIssue(
                    PrerequisiteIssueSeverity.ERROR,
                    PrerequisiteIssueType.BINARY_ERROR,
                    f"{f.__name__} : {e!s}",
                )
                missing.append(m)
        logging.getLogger(wgse.utility.external.__name__).setLevel(old_level)
        return missing


if __name__ == "__main__":
    failing = CheckPrerequisites().check_prerequisites()
    if len(failing) == 0:
        print("All requirements are satisfied")
    else:
        for req in failing:
            print(req)
