import pytest
from pathlib import Path
from backend.app.config import settings
from scripts.backup import create_backup, restore_backup

def test_backup_and_restore(tmp_path):
    # Setup temporary paths
    test_db = tmp_path / "nfm.db"
    test_vectors = tmp_path / "vectors"

    # Create dummy files
    test_db.write_text("dummy database content")
    test_vectors.mkdir(parents=True, exist_ok=True)
    (test_vectors / "dummy_index.faiss").write_text("dummy vector index data")

    # Store original paths
    original_db = settings.NFM_DB_PATH
    original_vectors = settings.NFM_VECTOR_PATH

    # Override config paths for testing
    settings.NFM_DB_PATH = test_db
    settings.NFM_VECTOR_PATH = test_vectors

    try:
        # Create backup
        backup_output = tmp_path / "backups"
        archive_path = create_backup(str(backup_output))

        assert Path(archive_path).exists()
        assert archive_path.endswith(".tar.gz")

        # Now corrupt/delete the dummy files
        test_db.write_text("corrupted content")
        import shutil
        shutil.rmtree(test_vectors)
        assert not test_vectors.exists()

        # Restore from backup
        res = restore_backup(archive_path)
        assert res is True

        # Verify restoration
        assert test_db.read_text() == "dummy database content"
        assert test_vectors.exists()
        assert (test_vectors / "dummy_index.faiss").read_text() == "dummy vector index data"

    finally:
        # Restore original paths
        settings.NFM_DB_PATH = original_db
        settings.NFM_VECTOR_PATH = original_vectors
