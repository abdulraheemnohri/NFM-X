#!/usr/bin/env python3
"""
NFM-X Python SDK
================

Python SDK for interacting with NFM-X memory system.
Provides client and models for easy integration.

Urdu: NFM-X میموری سسٹم کے ساتھ تعامل کے لیے پائتھن SDK
"""

from .nfm import client, models

__version__ = "0.1.0"
__all__ = ['client', 'models']


# Urdu Documentation
"""
 NFM-X پائتھن SDK
 ===============

 یہ NFM-X میموری سسٹم کے ساتھ تعامل کے لیے پائتھن SDK ہے۔
 
 استعمال:
 ```python
 from nfm import client, models
 
 # کلائنٹ بنائیں
 nfm_client = client.NFMClient(base_url="http://localhost:8000")
 
 # نئی میموری شامل کریں
 memory = models.MemoryCreate(
     content="میں نے آج پی ایچ ڈی کے لیے درخواست دی",
     memory_type="episodic"
 )
 result = nfm_client.create_memory(memory)
 print(f"Memory ID: {result.id}")
 ```
"""