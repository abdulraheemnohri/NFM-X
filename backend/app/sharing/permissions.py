"""NFM-X V3 Sharing Permissions
Manages read, write, and admin permissions for shared memory bundles"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)


@dataclass
class PermissionSet:
    """Permissions for a user on a bundle"""
    user_id: str
    read: bool = False
    write: bool = False
    admin: bool = False
    granted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    granted_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "read": self.read,
            "write": self.write,
            "admin": self.admin,
            "granted_at": self.granted_at.isoformat(),
            "granted_by": self.granted_by
        }
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        if permission == "admin":
            return self.admin
        elif permission == "write":
            return self.write or self.admin
        elif permission == "read":
            return self.read or self.write or self.admin
        return False
    
    def can_grant(self, permission: str) -> bool:
        """Check if user can grant a permission to others"""
        if self.admin:
            return True
        return False


@dataclass
class SharingBundle:
    """A bundle of memories that can be shared"""
    bundle_id: str
    name: str
    description: str = ""
    memory_ids: Set[str] = field(default_factory=set)
    owner_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    permissions: Dict[str, PermissionSet] = field(default_factory=dict)
    is_public: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_memory(self, memory_id: str) -> None:
        """Add a memory to the bundle"""
        self.memory_ids.add(memory_id)
        self.updated_at = datetime.now(timezone.utc)
    
    def remove_memory(self, memory_id: str) -> bool:
        """Remove a memory from the bundle"""
        if memory_id in self.memory_ids:
            self.memory_ids.remove(memory_id)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def grant_permission(self, user_id: str, read: bool, write: bool, admin: bool, granted_by: str) -> None:
        """Grant permissions to a user"""
        self.permissions[user_id] = PermissionSet(
            user_id=user_id,
            read=read,
            write=write,
            admin=admin,
            granted_by=granted_by
        )
        self.updated_at = datetime.now(timezone.utc)
        logger.info(f"Granted permissions to {user_id} on bundle {self.bundle_id}")
    
    def revoke_permission(self, user_id: str) -> bool:
        """Revoke all permissions from a user"""
        if user_id in self.permissions:
            del self.permissions[user_id]
            self.updated_at = datetime.now(timezone.utc)
            logger.info(f"Revoked permissions from {user_id} on bundle {self.bundle_id}")
            return True
        return False
    
    def update_permission(self, user_id: str, read: Optional[bool] = None, write: Optional[bool] = None, admin: Optional[bool] = None) -> bool:
        """Update specific permissions for a user"""
        if user_id not in self.permissions:
            return False
        
        perm = self.permissions[user_id]
        if read is not None:
            perm.read = read
        if write is not None:
            perm.write = write
        if admin is not None:
            perm.admin = admin
        
        self.updated_at = datetime.now(timezone.utc)
        logger.info(f"Updated permissions for {user_id} on bundle {self.bundle_id}")
        return True
    
    def can_access(self, user_id: str, permission: str) -> bool:
        """Check if a user has a specific permission"""
        if user_id == self.owner_id:
            return True  # Owner has all permissions
        
        if self.is_public and permission == "read":
            return True
        
        perm = self.permissions.get(user_id)
        if perm:
            return perm.has_permission(permission)
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "name": self.name,
            "description": self.description,
            "memory_ids": list(self.memory_ids),
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "permissions": {uid: p.to_dict() for uid, p in self.permissions.items()},
            "is_public": self.is_public,
            "metadata": self.metadata
        }


class SharingPermissionManager:
    """Manages sharing permissions for memory bundles"""
    
    def __init__(self):
        self.bundles: Dict[str, SharingBundle] = {}
    
    def create_bundle(
        self,
        name: str,
        owner_id: str,
        memory_ids: Optional[List[str]] = None,
        description: str = "",
        is_public: bool = False
    ) -> SharingBundle:
        """Create a new sharing bundle"""
        bundle = SharingBundle(
            bundle_id=str(uuid.uuid4()),
            name=name,
            description=description,
            memory_ids=set(memory_ids or []),
            owner_id=owner_id,
            is_public=is_public
        )
        
        # Grant owner full permissions
        bundle.grant_permission(owner_id, read=True, write=True, admin=True, granted_by="system")
        
        self.bundles[bundle.bundle_id] = bundle
        logger.info(f"Created bundle: {bundle.bundle_id} by {owner_id}")
        return bundle
    
    def get_bundle(self, bundle_id: str) -> Optional[SharingBundle]:
        """Get a bundle by ID"""
        return self.bundles.get(bundle_id)
    
    def delete_bundle(self, bundle_id: str, user_id: str) -> bool:
        """Delete a bundle (only owner or admin can delete)"""
        bundle = self.bundles.get(bundle_id)
        if not bundle:
            return False
        
        if bundle.owner_id != user_id and not bundle.can_access(user_id, "admin"):
            return False
        
        del self.bundles[bundle_id]
        logger.info(f"Deleted bundle: {bundle_id} by {user_id}")
        return True
    
    def update_bundle_permissions(
        self,
        bundle_id: str,
        user_id: str,
        target_user_id: str,
        read: Optional[bool] = None,
        write: Optional[bool] = None,
        admin: Optional[bool] = None
    ) -> bool:
        """Update permissions for a user on a bundle"""
        bundle = self.bundles.get(bundle_id)
        if not bundle:
            return False
        
        # Check if user has permission to grant permissions
        if not bundle.can_access(user_id, "admin"):
            return False
        
        if read is not None or write is not None or admin is not None:
            return bundle.update_permission(target_user_id, read, write, admin)
        
        return False
    
    def list_bundles(self, user_id: Optional[str] = None) -> List[SharingBundle]:
        """List all bundles, optionally filtered by user access"""
        if user_id:
            return [
                b for b in self.bundles.values()
                if b.owner_id == user_id or b.can_access(user_id, "read")
            ]
        return list(self.bundles.values())
    
    def get_user_bundles(self, user_id: str) -> List[SharingBundle]:
        """Get all bundles owned by a user"""
        return [b for b in self.bundles.values() if b.owner_id == user_id]