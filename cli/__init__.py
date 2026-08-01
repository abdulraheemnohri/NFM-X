#!/usr/bin/env python3
"""
NFM-X CLI
=========

Command-line interface for NFM-X memory system.

Urdu: NFM-X میموری سسٹم کے لیے کمانڈ لائن انٹرفیس
"""

from .main import main

__all__ = ['main']


# Urdu Documentation
"""
 NFM-X CLI
 ========

 یہ NFM-X میموری سسٹم کے لیے کمانڈ لائن انٹرفیس فراہم کرتا ہے۔
 
 استعمال:
 ```bash
 # مدد حاصل کریں
 nfm-x --help
 
 # میموری کی فہرست دیکھیں
 nfm-x memory list
 
 # نئی میموری شامل کریں
 nfm-x memory create --content "میں نے آج پی ایچ ڈی کے لیے درخواست دی" --type episodic
 
 # میموری تلاش کریں
 nfm-x search "پی ایچ ڈی"
 
 # سسٹم کی معلومات حاصل کریں
 nfm-x info
 ```
"""