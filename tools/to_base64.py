import base64
from pathlib import Path
import sys

if len(sys.argv) < 2:
    exit()
path = Path(sys.argv[1])
with path.open("rb") as f:
    b = f.read()
    print(f'"{path.name}" : "{base64.standard_b64encode(b).decode("utf-8")}"')
