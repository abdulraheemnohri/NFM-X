"""
SQLAlchemy models for NFM-X
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Index, Enum, func
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum as PyEnum
from ..storage.database import Base

class MemoryType(str, PyEnum):
    FACT = "fact"; CONCEPT = "concept"; PROCEDURE = "procedure"; EXPERIENCE = "experience"; CAUSAL = "causal"; DECISION = "decision"; OBSERVATION = "observation"; HYPOTHESIS = "hypothesis"; GOAL = "goal"; PLAN = "plan"

class MemoryStatus(str, PyEnum):
    ACTIVE = "active"; ARCHIVED = "archived"; DELETED = "deleted"; WORKING = "working"

class EventType(str, PyEnum):
    CREATED = "created"; UPDATED = "updated"; VERSIONED = "versioned"; DELETED = "deleted"; RESTORED = "restored"; ARCHIVED = "archived"; TAGGED = "tagged"; RELATED = "related"; CONFLICT = "conflict"; CONSOLIDATED = "consolidated"

class RelationshipType(str, PyEnum):
    RELATED = "related"; SUBSUMES = "subsumes"; CONTRADICTS = "contradicts"; SUPPORTS = "supports"; EXTENDS = "extends"; SPECIALIZES = "specializes"; GENERALIZES = "generalizes"; CAUSES = "causes"; PRECEDES = "precedes"; DEPENDS_ON = "depends_on"

class ChangeType(str, PyEnum):
    CORRECT = "correct"; REFINES = "refine"; EXPAND = "expand"; SUPERSEDE = "supersede"; CLARIFY = "clarify"; SIMPLIFY = "simplify"