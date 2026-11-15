"""Archive committed project files; never include local credentials or dependencies."""
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parents[2]
destination=root/'analysis/validation/reports/EarthSignal-source.zip'
destination.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['git','archive','--format=zip','--prefix=EarthSignal/',f'--output={destination}','HEAD'],cwd=root,check=True)
print(destination)
