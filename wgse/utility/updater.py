import subprocess
import sys
from importlib.metadata import version


class Updater:

    def __init__(self) -> None:
        self.packages = ["WGSE-NG", "WGSE-NG-3rd-party"]
        # Package Name -> (Current v., Latest v.)
        self.versions = {x: (version(x), self.check(x)) for x in self.packages}

    def check(self, package_name):
        latest_version = subprocess.check_output(
            [sys.executable, "-m", "pip", "index", "versions", package_name]
        ).decode("utf-8")
        latest_version = latest_version.split("Version: ")[1].split("\n")[0]
        return latest_version

    def update(self, package_name, versions):
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
        )
        print(f"Upgraded {package_name} from {versions[0]} to {versions[1]}")

        sys.exit()


if __name__ == "__main__":
    a = Updater()
    pass
