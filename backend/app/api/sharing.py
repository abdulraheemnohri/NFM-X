"""NFM-X V3 Sharing API
Manages sharing bundles and permissions"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from backend.app.sharing.permissions import SharingPermissionManager, SharingBundle

router = APIRouter(prefix="", tags=["Sharing"])


class CreateBundleRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    memory_ids: Optional[List[str]] = None
    is_public: Optional[bool] = False


class UpdateBundleRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class PermissionUpdateRequest(BaseModel):
    read: Optional[bool] = None
    write: Optional[bool] = None
    admin: Optional[bool] = None


class BundleResponse(BaseModel):
    bundle_id: str
    name: str
    description: str
    memory_ids: List[str]
    owner_id: str
    created_at: str
    updated_at: str
    is_public: bool
    permissions: Dict[str, Dict[str, Any]]


# Initialize permission manager
sharing_manager = SharingPermissionManager()


@router.post("/bundles", response_model=BundleResponse, status_code=201)
async def create_bundle(request: CreateBundleRequest, user_id: str = "system"):
    """
    Create a new sharing bundle
    """
    bundle = sharing_manager.create_bundle(
        name=request.name,
        owner_id=user_id,
        memory_ids=request.memory_ids or [],
        description=request.description or "",
        is_public=request.is_public or False
    )
    
    return BundleResponse(
        bundle_id=bundle.bundle_id,
        name=bundle.name,
        description=bundle.description,
        memory_ids=list(bundle.memory_ids),
        owner_id=bundle.owner_id,
        created_at=bundle.created_at.isoformat(),
        updated_at=bundle.updated_at.isoformat(),
        is_public=bundle.is_public,
        permissions={uid: p.to_dict() for uid, p in bundle.permissions.items()}
    )



@router.get("/bundles", response_model=List[BundleResponse])
async def list_bundles(user_id: Optional[str] = None):
    """
    List all sharing bundles
    """
    bundles = sharing_manager.list_bundles(user_id)
    return [
        BundleResponse(
            bundle_id=b.bundle_id,
            name=b.name,
            description=b.description,
            memory_ids=list(b.memory_ids),
            owner_id=b.owner_id,
            created_at=b.created_at.isoformat(),
            updated_at=b.updated_at.isoformat(),
            is_public=b.is_public,
            permissions={uid: p.to_dict() for uid, p in b.permissions.items()}
        )
        for b in bundles
    ]


@router.get("/bundles/{bundle_id}", response_model=BundleResponse)
async def get_bundle(bundle_id: str, user_id: Optional[str] = None):
    """
    Get a specific sharing bundle
    """
    bundle = sharing_manager.get_bundle(bundle_id)
    if not bundle:
        raise HTTPException(status_code=404, detail=f"Bundle {bundle_id} not found")
    
    # Check access
    if user_id and not bundle.can_access(user_id, "read") and bundle.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return BundleResponse(
        bundle_id=bundle.bundle_id,
        name=bundle.name,
        description=bundle.description,
        memory_ids=list(bundle.memory_ids),
        owner_id=bundle.owner_id,
        created_at=bundle.created_at.isoformat(),
        updated_at=bundle.updated_at.isoformat(),
        is_public=bundle.is_public,
        permissions={uid: p.to_dict() for uid, p in bundle.permissions.items()}
    )


@router.put("/bundles/{bundle_id}/permissions/{user_id}", status_code=200)
async def update_permissions(
    bundle_id: str,
    user_id: str,
    target_user_id: str,
    request: PermissionUpdateRequest,
    current_user: str = "system"
):
    """
    Update permissions for a user on a bundle
    
    Only bundle owner or admin can update permissions
    "
""
    success = sharing_manager.update_bundle_permissions(
        bundle_id=bundle_id,
        user_id=current_user,
        target_user_id=target_user_id,
        read=request.read,
        write=request.write,
        admin=request.admin
    )
    
    if not success:
        raise HTTPException(status_code=403, detail="Permission denied or user not found")
    
    return {"message": f"Permissions updated for {target_user_id} on bundle {bundle_id}"}


@router.delete("/bundles/{bundle_id}", status_code=200)
async def delete_bundle(bundle_id: str, user_id: str = "system"):
    """
    Delete a sharing bundle
    
    Only bundle owner or admin can delete
    """
    success = sharing_manager.delete_bundle(bundle_id, user_id)
    if not success:
        raise HTTPException(status_code=403, detail="Permission denied or bundle not found")
    
    return {"message": f"Bundle {bundle_id} deleted successfully"}