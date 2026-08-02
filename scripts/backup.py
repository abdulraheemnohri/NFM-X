import json
import shutil
import tarfile
from pathlib import Path
from datetime import datetime, timezone

from backend.app.config import settings

def create_backup(output_dir: str = "./backups") -> str:
    """Create a full backup of database and vector index."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_name = f"nfm_backup_{timestamp}"
    backup_dir = output_path / backup_name
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Copy database
    if settings.NFM_DB_PATH.exists():
        shutil.copy2(settings.NFM_DB_PATH, backup_dir / "nfm.db")

    # Copy vector index
    if settings.NFM_VECTOR_PATH.exists():
        vector_backup = backup_dir / "vectors"
        shutil.copytree(settings.NFM_VECTOR_PATH, vector_backup)

    # Create manifest
    manifest = {
        "version": "1.5.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "nfm.db",
        "vectors": "vectors/"
    }
    with open(backup_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Create tar archive
    archive_path = output_path / f"{backup_name}.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(backup_dir, arcname=backup_name)

    # Clean up temp dir
    shutil.rmtree(backup_dir)

    return str(archive_path)

def restore_backup(archive_path: str) -> bool:
    """Restore from a backup archive."""
    archive = Path(archive_path)
    if not archive.exists():
        raise FileNotFoundError(f"Backup not found: {archive_path}")

    # Extract
    extract_dir = Path("./backups/restore_temp")
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True)

    with tarfile.open(archive, "r:gz") as tar:
        tar.extractall(extract_dir)

    # Find extracted dir (there might be nested folders or directly the temp backup_name dir)
    extracted = None
    for item in extract_dir.iterdir():
        if item.is_dir():
            extracted = item
            break

    if not extracted:
        extracted = extract_dir

    # Validate manifest
    manifest_path = extracted / "manifest.json"
    if not manifest_path.exists():
        shutil.rmtree(extract_dir)
        raise ValueError("Invalid backup: manifest.json missing")

    with open(manifest_path) as f:
        manifest = json.load(f)

    # Restore database
    db_backup = extracted / manifest["database"]
    if db_backup.exists():
        settings.NFM_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(db_backup, settings.NFM_DB_PATH)

    # Restore vectors
    vector_backup = extracted / manifest["vectors"]
    if vector_backup.exists():
        if settings.NFM_VECTOR_PATH.exists():
            shutil.rmtree(settings.NFM_VECTOR_PATH)
        settings.NFM_VECTOR_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(vector_backup, settings.NFM_VECTOR_PATH)

    # Cleanup
    shutil.rmtree(extract_dir)
    return True
