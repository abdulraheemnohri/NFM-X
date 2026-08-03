"""Tests for NFM-X V3 Compression Scheduler"""

import pytest
from backend.app.compression.scheduler import CompressionScheduler, CompressionConfig


class TestCompressionV3:
    def test_config_defaults(self):
        """Test default configuration"""
        config = CompressionConfig()
        assert config.enabled is True
        assert config.age_days == 30
        assert config.importance_threshold == 0.5
        assert config.run_interval_hours == 24
        assert config.max_memories_per_run == 100
    
    def test_config_from_env(self):
        """Test configuration from environment"""
        import os
        os.environ["NFM_COMPRESSION_ENABLED"] = "false"
        os.environ["NFM_COMPRESSION_AGE_DAYS"] = "60"
        
        config = CompressionConfig.from_env()
        assert config.enabled is False
        assert config.age_days == 60
    
    def test_scheduler_init(self):
        """Test scheduler initialization"""
        config = CompressionConfig(enabled=True, age_days=30)
        scheduler = CompressionScheduler(config)
        assert scheduler.config.enabled is True
    
    def test_is_eligible_for_compression(self):
        """Test compression eligibility"""
        config = CompressionConfig(age_days=30, importance_threshold=0.5)
        scheduler = CompressionScheduler(config)
        
        from datetime import datetime, timedelta
        now = datetime.now(timezone.utc)()
        old_date = now - timedelta(days=40)
        
        # Old and low importance - eligible
        memory1 = {"id": "mem_1", "importance": 0.3, "created_at": old_date.isoformat()}
        assert scheduler._is_eligible_for_compression(memory1) is True
        
        # Recent but low importance - not eligible
        memory2 = {"id": "mem_2", "importance": 0.3, "created_at": now.isoformat()}
        assert scheduler._is_eligible_for_compression(memory2) is False
        
        # Old but high importance - not eligible
        memory3 = {"id": "mem_3", "importance": 0.8, "cr
eated_at": old_date.isoformat()}
        assert scheduler._is_eligible_for_compression(memory3) is False
    
    def test_is_eligible_for_archive(self):
        """Test archive eligibility"""
        config = CompressionConfig(archive_enabled=True, archive_age_days=90)
        scheduler = CompressionScheduler(config)
        
        from datetime import datetime, timedelta
        now = datetime.now(timezone.utc)()
        old_date = now - timedelta(days=100)
        recent_date = now - timedelta(days=80)
        
        # Very old - eligible
        memory1 = {"id": "mem_1", "created_at": old_date.isoformat()}
        assert scheduler._is_eligible_for_archive(memory1) is True
        
        # Not old enough - not eligible
        memory2 = {"id": "mem_2", "created_at": recent_date.isoformat()}
        assert scheduler._is_eligible_for_archive(memory2) is False
    
    def test_get_config(self):
        """Test getting configuration"""
        config = CompressionConfig(enabled=False)
        scheduler = CompressionScheduler(config)
        
        retrieved_config = scheduler.get_config()
        assert retrieved_config.enabled is False
    
    def test_update_config(self):
        """Test updating configuration"""
        scheduler = CompressionScheduler()
        
        updated = scheduler.update_config(age_days=60, importance_threshold=0.3)
        assert updated.age_days == 60
        assert updated.importance_threshold == 0.3
    
    def test_run_history(self):
        """Test run history tracking"""
        config = CompressionConfig(enabled=False)
        scheduler = CompressionScheduler(config)
        
        history = scheduler.get_run_history()
        assert len(history) == 0
    
    def test_current_run(self):
        """Test current run tracking"""
        scheduler = CompressionScheduler()
        
        current = scheduler.get_current_run()
        assert current is None