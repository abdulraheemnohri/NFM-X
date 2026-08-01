"""
NFM-X Procedural Memory Module

Stores and improves procedures for performing tasks.

Procedural learning loop:
Attempt -> Result -> Evaluation -> Procedure Update

Repeated successful execution creates improved procedures.
"""

from .procedure_store import ProcedureStore
from .procedure_learner import ProcedureLearner
from .procedure_executor import ProcedureExecutor

__all__ = ['ProcedureStore', 'ProcedureLearner', 'ProcedureExecutor']