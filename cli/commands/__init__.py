"""
NFM-X CLI Commands Package

This package contains all the command implementations for the NFM-X CLI.
Each command module provides specific functionality for managing the NFM-X memory layer.
"""

from .status import StatusCommand
from .memory import MemoryCommand
from .graph import GraphCommand
from .conflicts import ConflictsCommand
from .skills import SkillsCommand
from .patterns import PatternsCommand
from .backup import BackupCommand
from .integrity import IntegrityCommand
from .server import ServerCommand

__all__ = [
    'StatusCommand',
    'MemoryCommand', 
    'GraphCommand',
    'ConflictsCommand',
    'SkillsCommand',
    'PatternsCommand',
    'BackupCommand',
    'IntegrityCommand',
    'ServerCommand'
]

COMMAND_CLASSES = {
    'status': StatusCommand,
    'memory': MemoryCommand,
    'graph': GraphCommand,
    'conflicts': ConflictsCommand,
    'skills': SkillsCommand,
    'patterns': PatternsCommand,
    'backup': BackupCommand,
    'integrity': IntegrityCommand,
    'server': ServerCommand
}

def get_command_class(command_name):
    """Get the command class for a given command name."""
    return COMMAND_CLASSES.get(command_name.lower())
