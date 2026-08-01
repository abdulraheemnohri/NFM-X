"""
NFM-X OCR Text Extraction Module
==================================

Text extraction functions for OCR results.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from .models import OCRLayout, OCRTextBlock, OCRLine, OCRParagraph, BoundingBox


def extract_text_and_layout(text: str, confidence: float = 1.0) -> OCRLayout:
    layout = OCRLayout()
    if not text or not text.strip():
        return layout
    
    lines_text = text.split('\n')
    word_count = 0
    
    for line_idx, line_text in enumerate(lines_text):
        if not line_text.strip():
            continue
        
        words = line_text.split()
        line_blocks = []
        
        for word_idx, word_text in enumerate(words):
            bbox = BoundingBox(x=word_idx * 50, y=line_idx * 30, width=len(word_text) * 15, height=25)
            block = OCRTextBlock(text=word_text, bounding_box=bbox, confidence=confidence)
            line_blocks.append(block)
            word_count += 1
        
        if line_blocks:
            line_bbox = BoundingBox(
                x=min(b.bounding_box.x for b in line_blocks),
                y=min(b.bounding_box.y for b in line_blocks),
                width=max(b.bounding_box.x2 for b in line_blocks) - min(b.bounding_box.x for b in line_blocks),
                height=25
            )
            line = OCRLine(blocks=line_blocks, bounding_box=line_bbox, line_number=line_idx)
            layout.lines.append(line)
        
        layout.text_blocks.extend(line_blocks)
    
    return layout


# Urdu: NFM-X OCR ٹیکسٹ ایکسٹرکشن ماڈول