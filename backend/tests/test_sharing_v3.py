"""Tests for NFM-X V3 Sharing Permissions"""

import pytest
from backend.app.sharing.permissions import SharingPermissionManager, SharingBundle, PermissionSet


class TestSharingV3:
    def test_create_bundle(self):
        """Test creating a sharing bundle"""
        manager = SharingPermissionManager()
        bundle = manager.create_bundle("Test Bundle", "user_1", ["mem_1", "mem_2"])
        
        assert bundle.bundle_id is not None
        assert bundle.name == "Test Bundle"
        assert bundle.owner_id == "user_1"
        assert len(bundle.memory_ids) == 2
    
    def test_grant_permission(self):
        """Test granting permissions"""
        manager = SharingPermissionManager()
        bundle = manager.create_bundle("Test Bundle", "user_1")
        
        bundle.grant_permission("user_2", read=True, write=False, admin=False, granted_by="user_1")
        
        assert "user_2" in bundle.permissions
        assert bundle.permissions["user_2"].read is True
        assert bundle.permissions["user_2"].write is False
    
    def test_revoke_permission(self):
        """Test revoking permissions"""
        manager = SharingPermissionManager()
        bundle = manager.create_bundle("Test Bundle", "user_1")
        bundle.grant_permission("user_2", read=True, write=True, admin=False, granted_by="user_1")
        
        result = bundle.revoke_permission("user_2")
        assert result is True
        assert "user_2" not in bundle.permissions
    
    def test_update_permission(self):
        """Test updating permissions"""
        manager = SharingPermissionManager()
        bundle = manager.create_bundle("Test Bundle", "user_1")
        bundle.grant_permission("user_2", read=True, write=False, admin=False, granted_by="user_1")
        
        result = bundle.update_permission("user_2", read=True, write=True, admin=False)
        assert result is True
        assert bundle.permissions["user_2"].write is True
    
    def test_can_access_owner(self):
        """Test owner access"""
        manager = SharingPermissionManager()
        bundle = manager.create_bundle("Test Bundle", "user_1")
        
        assert bundle.can_access("user_1", "read") is True
        assert bundle.can_access("user_1", "write") is True
        assert bundle.can_access("user_1", "admin") is True
    
    def test_can_access_with_permission(self):
        """Test access with granted permissions"""
        manager = SharingPermissionManager()
        bundle = manager.create_bundle("Test Bundle", "user_1")
        bundle.grant_permission("user_2", read=True, write=False, admin=False, granted_by="user_1")
        
        assert bundle.can_access("user_2", "read") is True
        assert bundle.can_access("user_2", "write") is False
        assert bundle.can_access("user_2", "admin") is False
    
    def test_can_access_public(self):
        """Test public bundle access"""
        manager = SharingPermissionManager()
        bundle = manager.create_bundle("Public Bundle", "user_1", is_public=True)
        
        assert bundle.can_access("any_user", "read") is True
        assert bundle.can_access("any_user", "write") is False
    
    def test_list_bundles(self):
        """Test listing bundles"""
        manager = SharingPermissionManager()
        manager.create_bundle("Bundle 1", "user_1")
        manager.create_bundle("Bundle 2", "user_2")
        
        bundles = manager.list_bundles()
        assert len(bundles) == 2
    
    def test_delete_bundle(self):
        """Test deleting a bundle"""
        manager = SharingPermissionManager()
        bundle = manager.create_bundle("Test Bundle", "user_1")
        
        result = manager.delete_bundle(bundle.bundle_id, "user_1")
        assert result is True
        
        assert manager.get_bundle(bundle.bundle_id) is None