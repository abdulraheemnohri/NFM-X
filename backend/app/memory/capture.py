"""
NFM-X Memory Capture
Captures and processes new memories from various sources
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import hashlib
import logging
import uuid

from .models import Memory, MemoryStatus, MemoryType, MemoryEvent, EventType
from .classification import classifier
from ..storage.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class MemoryCapture:
    def __init__(self):
        self.classifier = classifier

    async def capture(
        self,
        content: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        source: Optional[str] = None,
        source_id: Optional[str] = None,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
        db_session = None
    ) -> Memory:
        # If no session provided, create a new one that we will manage
        session_owner = db_session is None
        # If no session provided, create a new one that we will manage
        session_owner = db_session is None
        if db_session is None:
            db_session = AsyncSessionLocal()
        
        try:
            memory = Memory(
                id=str(uuid.uuid4()),
                content=content,
                content_hash=self._compute_hash(content),
                title=title or self._extract_title(content),
                description=description,
                memory_type=memory_type or MemoryType.TEXT,
                source=source or "api",
                source_id=source_id,
                author=author or "system",
                tags=tags or [],
                categories=categories or [],
                metadata=metadata or {},
                parent_id=parent_id,
                status=MemoryStatus.ACTIVE,
                version=1
            )
            
            memory = self.classifier.classify_memory(memory)
            
            if parent_id:
                from sqlalchemy import select
                result = await
 db_session.execute(
                    select(Memory).where(Memory.id == parent_id)
                )
                parent = result.scalar_one_or_none()
                if parent:
                    memory.version = parent.version + 1
                    parent.status = MemoryStatus.ARCHIVED
                    parent.archived_at = datetime.now(timezone.utc)
                    
                    version_event = MemoryEvent(
                        memory_id=parent.id,
                        event_type=EventType.VERSIONED,
                        details={"new_version_id": memory.id, "new_version": memory.version}
                    )
                    db_session.add(version_event)
            
            db_session.add(memory)
            
            creation_event = MemoryEvent(
                memory_id=memory.id,
                event_type=EventType.CREATED,
                details={"source": memory.source, "author": memory.author}
            )
            db_session.add(creation_event)
            
            await db_session.commit()
            await db_session.refresh(memory)
            
            logger.info(f"Captured memory {memory.id} (v{memory.version})")
            return memory
            
        except Exception as e:
            await db_session.rollback()
            logger.error(f"Failed to capture memory: {e}")
            raise
        finally:
            # Only close the session if we created it
            if session_owner and db_session is not None:
                await db_session.close()

    async def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db_session = None
    ) -> Memory:
        from sqlalchemy import select
        
        if db_session is None:
            db_session = AsyncSessionLocal()
        
        
try:
            result = await db_session.execute(
                select(Memory).where(Memory.id == memory_id)
            )
            current_memory = result.scalar_one_or_none()
            
            if not current_memory:
                raise ValueError(f"Memory {memory_id} not found")
            
            content_changed = content is not None and content != current_memory.content
            
            if content_changed:
                return await self.capture(
                    content=content,
                    title=title or current_memory.title,
                    description=description or current_memory.description,
                    memory_type=current_memory.memory_type,
                    source="update",
                    source_id=current_memory.id,
                    author=current_memory.author,
                    tags=tags or current_memory.tags,
                    categories=categories or current_memory.categories,
                    metadata=metadata or current_memory.metadata,
                    parent_id=memory_id,
                    db_session=db_session
                )
            else:
                if title is not None:
                    current_memory.title = title
                if description is not None:
                    current_memory.description = description
                if tags is not None:
                    current_memory.tags = tags
                if categories is not None:
                    current_memory.categories = categories
                if metadata is not None:
                    current_memory.metadata.update(metadata or {})
                
                current_memory.updated_at = datetime.now(timezone.utc)
                
                update_event = MemoryEvent(
                    memory_id=memory_id,
                    event_type=EventType.UPDATED,
                    details={"fields": {"title": title is not None, "description": description is not None}}
  
              )
                db_session.add(update_event)
                
                await db_session.commit()
                await db_session.refresh(current_memory)
                return current_memory
                
        except Exception as e:
            await db_session.rollback()
            logger.error(f"Failed to update memory {memory_id}: {e}")
            raise
        finally:
            # Only close the session if we created it
            if session_owner and db_session is not None:
                await db_session.close()

    async def delete_memory(
        self,
        memory_id: str,
        hard_delete: bool = False,
        db_session = None
    ) -> bool:
        from sqlalchemy import select
        
        if db_session is None:
            db_session = AsyncSessionLocal()
        
        try:
            result = await db_session.execute(
                select(Memory).where(Memory.id == memory_id)
            )
            memory = result.scalar_one_or_none()
            
            if not memory:
                raise ValueError(f"Memory {memory_id} not found")
            
            if hard_delete:
                await db_session.delete(memory)
                await db_session.execute(
                    MemoryEvent.__table__.delete().where(MemoryEvent.memory_id == memory_id)
                )
            else:
                memory.status = MemoryStatus.DELETED
                memory.deleted_at = datetime.now(timezone.utc)
                
                delete_event = MemoryEvent(
                    memory_id=memory_id,
                    event_type=EventType.DELETED,
                    details={"hard_delete": False}
                )
                db_session.add(delete_event)
            
            await db_session.commit()
            return True
            
        except Exception as e:
            await db_session.rollback()
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            raise
        finally:
            # Only close the session if we created it
            if session_owner and db_session is not None:
                await db_session.close()

    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _extract_title(self, content: str, max_length: int = 100) -> str:
        content = content.strip()
        lines = content.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line:
                if line.startswith('#'):
                    line = line.lstrip('#').strip()
                line = line.strip(' #*_\n\t')
                if line:
                    return line[:max_length]
        return content[:max_length] if content else "Untitled"


capture = MemoryCapture()