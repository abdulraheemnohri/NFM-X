#!/usr/bin/env python3
"""
NFM-X CLI Main Entry Point

This is the main entry point for the NFM-X command line interface.
It provides a comprehensive CLI for managing the NFM-X memory layer.
"""

import argparse
import sys
import os
from commands import COMMAND_CLASSES


def create_parser():
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog='nfm',
        description='NFM-X (Non-Forgettable Memory Layer) - Command Line Interface',
        epilog='Use "nfm <command> --help" for more information about a command.'
    )
    
    # Add version argument
    parser.add_argument(
        '--version',
        '-v',
        action='version',
        version='NFM-X CLI v1.0.0'
    )
    
    # Create subparsers for each command
    subparsers = parser.add_subparsers(
        dest='command',
        title='commands',
        description='Available NFM-X commands'
    )
    
    # Register all command classes
    for command_name, command_class in COMMAND_CLASSES.items():
        command = command_class()
        command.add_parser(subparsers)
    
    return parser


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # If no command provided, show help
    if not hasattr(args, 'command') or args.command is None:
        parser.print_help()
        return 1
    
    # Get the command class
    command_class = COMMAND_CLASSES.get(args.command)
    if command_class is None:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        return 1
    
    # Create command instance and execute
    command = command_class()
    try:
        return command.execute(args)
    except Exception as e:
        print(f"Error executing command '{args.command}': {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())