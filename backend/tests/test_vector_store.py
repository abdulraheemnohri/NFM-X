import pytest
import os
import shutil
from backend.app.embeddings.vector_store import FAISSVectorStore

def test_vector_store_operations():
    test_dir = "./storage/test_vectors"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    store = FAISSVectorStore(dimension=4, index_path=test_dir)
    assert store._count == 0

    # Add vectors
    store.add("mem-1", "Hello world", [1.0, 0.0, 0.0, 0.0], {"tag": "greeting"})
    store.add("mem-2", "Python code", [0.0, 1.0, 0.0, 0.0], {"tag": "tech"})
    assert store._count == 2

    # Search L2 / inner product (FlatIP)
    # Norm of vectors is 1.0, query [1.0, 0.0, 0.0, 0.0] should perfectly match mem-1 (score ~1.0)
    results = store.search([1.0, 0.0, 0.0, 0.0], k=2)
    assert len(results) == 2
    assert results[0]["memory_id"] == "mem-1"
    assert abs(results[0]["score"] - 1.0) < 1e-5

    # Soft delete
    assert store.delete("mem-2") is True
    assert store._metadata["mem-2"]["_deleted"] is True

    # Save and Load
    store.save()
    assert os.path.exists(os.path.join(test_dir, "index.faiss"))
    assert os.path.exists(os.path.join(test_dir, "meta.json"))

    loaded_store = FAISSVectorStore(dimension=4, index_path=test_dir)
    loaded_store.load()
    assert loaded_store._count == 2
    assert loaded_store._id_map[0] == "mem-1"
    assert loaded_store._id_map[1] == "mem-2"
    assert loaded_store._metadata["mem-2"]["_deleted"] is True

    # Cleanup
    shutil.rmtree(test_dir)
