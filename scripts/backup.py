import os
import tarfile
import shutil
from pathlib import Path
from backend.app.config import settings

def create_backup(backup_output_dir: str) -> str:
    db_path = Path(settings.NFM_DB_PATH)
    vector_path = Path(settings.NFM_VECTOR_PATH)

    output_dir = Path(backup_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    archive_path = output_dir / "backup.tar.gz"

    with tarfile.open(archive_path, "w:gz") as tar:
        if db_path.exists():
            tar.add(db_path, arcname=db_path.name)
        if vector_path.exists():
            tar.add(vector_path, arcname=vector_path.name)

    return str(archive_path)

def restore_backup(archive_path: str) -> bool:
    db_path = Path(settings.NFM_DB_PATH)
    vector_path = Path(settings.NFM_VECTOR_PATH)

    # Remove existing
    if db_path.exists():
        db_path.unlink()
    if vector_path.exists():
        if vector_path.is_file():
            vector_path.unlink()
        else:
            shutil.rmtree(vector_path)

    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=db_path.parent)

    return True
