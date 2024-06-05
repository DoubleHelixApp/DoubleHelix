import subprocess
import sys
from xml.etree import ElementTree

import requests
from packaging.version import Version

from helix import VERSION


class Updater:

    def __init__(self) -> None:
        self.packages = ["doublehelix", "doublehelix-external"]

    def check(self, stable_only=False):
        r = requests.get("https://pypi.org/rss/project/doublehelix/releases.xml")
        r.raise_for_status()
        rss_feed = ElementTree.fromstring(r.text)
        channel = rss_feed.find("channel")
        versions = []
        for item in channel.findall("item"):
            title = item.find("title").text
            version = Version(title)
            versions.append(version)

        if stable_only:
            filtered_versions = []
            for version in versions:
                v = Version(version)
                if v.is_devrelease or v.is_postrelease or v.is_prerelease:
                    continue
                filtered_versions.append(version)
            versions = filtered_versions

        if len(versions) == 0:
            return None

        versions.sort()

        latest = versions[-1]
        current = Version(VERSION.version)

        # In case you're using a dev version of a public release, that's the most
        # recent one.
        if latest.pre == current.pre and latest.base_version == current.base_version:
            return None

        if latest > current:
            return latest
        return None

    def update(self, package_name, versions):
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                f"{package_name}=={versions}",
            ]
        )
        print(f"Upgraded {package_name} from {versions[0]} to {versions[1]}")

        sys.exit()


if __name__ == "__main__":
    updater = Updater()
    latest = updater.check()
    if latest is not None:
        updater.update(latest)
