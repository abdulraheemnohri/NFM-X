from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select, func
import uuid

from ..storage.database import get_db_session
from ..memory.models import Memory, MemoryCheckpoint, MemoryStatus
from ..crypto.integrity import IntegrityChain
from ..crypto.merkle import MerkleTree
from ..crypto.signatures import MemorySigner

router = APIRouter()

class CheckpointResponse(BaseModel):
    id: str
    checkpoint_type: str
    merkle_root: Optional[str] = None
    memory_count: int
    created_at: str
    signature: Optional[str] = None

@router.post("/checkpoints/create")
async def create_checkpoint(db_session=Depends(get_db_session)):
    """Create a cryptographic checkpoint of all active memories."""
    stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE).order_by(Memory.created_at)
    result = await db_session.execute(stmt)
    memories = result.scalars().all()

    if not memories:
        raise HTTPException(status_code=400, detail="No active memories to checkpoint")

    # Build integrity chain
    chain = IntegrityChain()
    hashes = []
    prev_hash = None
    for mem in memories:
        mem_hash = chain.hash_memory({
            "id": mem.id,
            "content": mem.content,
            "type": mem.memory_type.value if hasattr(mem.memory_type, "value") else str(mem.memory_type),
            "confidence": mem.confidence,
            "created_at": mem.created_at.isoformat()
        }, prev_hash)
        hashes.append(mem_hash)
        prev_hash = mem_hash

    # Build Merkle tree
    merkle = MerkleTree(hashes)

    # Sign checkpoint
    signer = MemorySigner()
    signature = signer.sign(merkle.root)

    checkpoint = MemoryCheckpoint(
        id=str(uuid.uuid4()), checkpoint_type="full",
        merkle_root=merkle.root, memory_count=len(memories),
        signature=signature, public_key=signer.get_public_key_pem(),
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(checkpoint)
    await db_session.commit()

    return CheckpointResponse(
        id=checkpoint.id, checkpoint_type="full",
        merkle_root=merkle.root, memory_count=len(memories),
        created_at=checkpoint.created_at.isoformat(),
        signature=signature
    )

@router.get("/checkpoints")
async def list_checkpoints(limit: int = 10, db_session=Depends(get_db_session)):
    stmt = select(MemoryCheckpoint).order_by(MemoryCheckpoint.created_at.desc()).limit(limit)
    result = await db_session.execute(stmt)
    checkpoints = result.scalars().all()
    return [CheckpointResponse(
        id=c.id, checkpoint_type=c.checkpoint_type,
        merkle_root=c.merkle_root, memory_count=c.memory_count,
        created_at=c.created_at.isoformat(), signature=c.signature
    ) for c in checkpoints]

@router.get("/checkpoints/{checkpoint_id}/verify")
async def verify_checkpoint(checkpoint_id: str, db_session=Depends(get_db_session)):
    """Verify a checkpoint against current memory state."""
    cp_result = await db_session.execute(select(MemoryCheckpoint).where(MemoryCheckpoint.id == checkpoint_id))
    checkpoint = cp_result.scalar_one_or_none()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE).order_by(Memory.created_at)
    result = await db_session.execute(stmt)
    memories = result.scalars().all()

    chain = IntegrityChain()
    hashes = []
    prev_hash = None
    for mem in memories:
        mem_hash = chain.hash_memory({
            "id": mem.id,
            "content": mem.content,
            "type": mem.memory_type.value if hasattr(mem.memory_type, "value") else str(mem.memory_type),
            "confidence": mem.confidence,
            "created_at": mem.created_at.isoformat()
        }, prev_hash)
        hashes.append(mem_hash)
        prev_hash = mem_hash

    merkle = MerkleTree(hashes)
    current_root = merkle.root

    # Verify signature
    signer = MemorySigner()
    signature_valid = signer.verify(checkpoint.merkle_root, checkpoint.signature, checkpoint.public_key)

    return {
        "checkpoint_id": checkpoint_id,
        "stored_root": checkpoint.merkle_root,
        "current_root": current_root,
        "roots_match": checkpoint.merkle_root == current_root,
        "signature_valid": signature_valid,
        "stored_memory_count": checkpoint.memory_count,
        "current_memory_count": len(memories),
        "verified_at": datetime.now(timezone.utc).isoformat()
    }
