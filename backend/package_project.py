"""Create a shareable source archive without installed packages or credentials."""
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[1]
destination=root.parent/'earthsignal-global-source.zip'
files=[]
for name in ('README.md','ARCHITECTURE.md','DESIGN_REVIEW.md','power-reference.json','NASA_REFERENCE.md','STUDY_VALIDATION.md','STUDY_WORKSPACE_VALIDATION.md','GLOBAL_SOURCE_AUDIT.md','AGENTS.md'):
    files.append(root/name)
for directory in ('backend','frontend','tests','worker','scripts'):
    for path in (root/directory).rglob('*'):
        relative=path.relative_to(root)
        if not path.is_file() or any(p in ('node_modules','__pycache__','.pytest_cache') for p in relative.parts):continue
        if path.name.startswith('.env') and path.name!='.env.example':continue
        files.append(path)
with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as archive:
    for path in files:archive.write(path,Path('earthsignal')/path.relative_to(root))
print(f'{destination} — {len(files)} files, {destination.stat().st_size} bytes')
