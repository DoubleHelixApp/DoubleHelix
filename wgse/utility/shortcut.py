import os
import platform
from pathlib import Path

try:
    from win32com.client import Dispatch
except Exception:
    pass
import importlib.metadata


class Shortcut:
    def __init__(self) -> None:
        distribution = importlib.metadata.distribution("WGSE-NG")
        entry_point = distribution.entry_points["wgse"]
        self.desktop = Path.home().joinpath("Desktop")
        self.path = None
        if len(entry_point.dist.files) > 0:
            self.path = entry_point.dist.locate_file(entry_point.dist.files[0])

    def _create_win(self):
        if self.path is None:
            return
        path = str(self.desktop.joinpath("WGSE-NG.lnk"))
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(path)
        shortcut.TargetPath = str(self.path)
        shortcut.WorkingDirectory = str(Path.home().joinpath("Documents"))
        shortcut.IconLocation = str(self.path)
        shortcut.Description = (
            "Genome file manipulation tool, https://github.com/WGSE-NG/WGSE-NG"
        )
        shortcut.save()
        return path

    def _create_mac(self):
        script = (
            'tell application "Finder"\n'
            + f'make alias file to POSIX file "{self.path!s}" at POSIX file "{self.desktop!s}"\n'
            + "end tell"
        )
        os.system(f"osascript -e '{script}'")
        return str(self.desktop)

    def _create_linux(self):
        if self.path is None:
            return
        shortcut_path = self.desktop.joinpath("WGSE-NG.desktop")
        desktop_entry = (
            "[Desktop Entry]\n"
            + "Type=Application\n"
            + "Name=WGSE-NG\n"
            + f"Exec={self.path!s}\n"
            + "Icon=\n"
            + "Terminal=false\n"
        )

        with shortcut_path.open("w") as file:
            file.write(desktop_entry)
        os.chmod(shortcut_path, 0o755)
        return str(shortcut_path)

    def create(self):
        os_type = platform.system()
        if os_type == "Windows":
            return self._create_win()
        elif os_type == "Linux":
            return self._create_linux()
        elif os_type == "Darwin":
            return self._create_mac()
        else:
            raise RuntimeError(f"Unsupported OS: {os_type}")
