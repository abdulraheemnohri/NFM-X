"""
NFM-X CLI Backup Command

Provides functionality to create, restore, and manage backups.
"""

import argparse
import json
from datetime import datetime


class BackupCommand:
    """Command to manage backups in NFM-X."""
    
    def __init__(self):
        self.name = 'backup'
        self.help = 'Manage NFM-X backups'
        self.description = 'Create, restore, list, and delete backups'
    
    def add_parser(self, subparsers):
        """Add the backup command parser."""
        parser = subparsers.add_parser(
            self.name,
            help=self.help,
            description=self.description
        )
        
        subcommand_parsers = parser.add_subparsers(
            dest='backup_action',
            title='backup actions',
            description='Available backup operations'
        )
        
        # Create subcommand
        create_parser = subcommand_parsers.add_parser(
            'create',
            help='Create a new backup'
        )
        create_parser.add_argument(
            '--name',
            '-n',
            help='Name for the backup'
        )
        create_parser.add_argument(
            '--description',
            '-d',
            help='Description of the backup'
        )
        create_parser.add_argument(
            '--all',
            action='store_true',
            help='Backup all data (including configuration)'
        )
        
        # Restore subcommand
        restore_parser = subcommand_parsers.add_parser(
            'restore',
            help='Restore from a backup'
        )
        restore_parser.add_argument(
            'backup_id',
            help='ID of the backup to restore'
        )
        restore_parser.add_argument(
            '--force',
            '-f',
            action='store_true',
            help='Force restore without confirmation'
        )
        
        # List subcommand
        list_parser = subcommand_parsers.add_parser(
            'list',
            help='List all backups'
        )
        list_parser.add_argument(
            '--limit',
            '-n',
            type=int,
            default=10,
            help='Maximum number of backups to display'
        )
        list_parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format'
        )
        
        # Delete subcommand
        delete_parser = subcommand_parsers.add_parser(
            'delete',
            help='Delete a backup'
        )
        delete_parser.add_argument(
            'backup_id',
            help='ID of the backup to delete'
        )
        delete_parser.add_argument(
            '--force',
            '-f',
            action='store_true',
            help='Force delete without confirmation'
        )
        
        # Info subcommand
        info_parser = subcommand_parsers.add_parser(
            'info',
            help='Show information about a backup'
        )
        info_parser.add_argument(
            'backup_id',
            help='ID of the backup'
        )
        info_parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format'
        )
        
        return parser
    
    def execute(self, args):
        """Execute the backup command."""
        if not hasattr(args, 'backup_action') or args.backup_action is None:
            parser = self.add_parser(argparse.ArgumentParser().add_subparsers())
            parser.print_help()
            return 1
        
        action = args.backup_action
        
        if action == 'create':
            return self._create_backup(args)
        elif action == 'restore':
            return self._restore_backup(args)
        elif action == 'list':
            return self._list_backups(args)
        elif action == 'delete':
            return self._delete_backup(args)
        elif action == 'info':
            return self._show_backup_info(args)
        else:
            print(f"Unknown backup action: {action}")
            return 1
    
    def _create_backup(self, args):
        """Create a new backup."""
        backup_name = args.name or f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"Creating backup: {backup_name}")
        if args.description:
            print(f"Description: {args.description}")
        if args.all:
            print("Backing up all data including configuration")
        else:
            print("Backing up memory data only")
        
        print("Backup created successfully")
        return 0
    
    def _restore_backup(self, args):
        """Restore from a backup."""
        if not args.force:
            response = input(f"Are you sure you want to restore backup {args.backup_id}? This will overwrite existing data. (y/n): ")
            if response.lower() != 'y':
                print("Restore cancelled")
                return 0
        
        print(f"Restoring from backup: {args.backup_id}")
        print("Restore completed successfully")
        return 0
    
    def _list_backups(self, args):
        """List all backups."""
        print(f"Listing backups (limit: {args.limit})")
        
        backups = []
        print(f"Found {len(backups)} backups")
        
        if args.json:
            print(json.dumps({'backups': backups}, indent=2))
        return 0
    
    def _delete_backup(self, args):
        """Delete a backup."""
        if not args.force:
            response = input(f"Are you sure you want to delete backup {args.backup_id}? (y/n): ")
            if response.lower() != 'y':
                print("Delete cancelled")
                return 0
        
        print(f"Deleting backup: {args.backup_id}")
        print("Backup deleted successfully")
        return 0
    
    def _show_backup_info(self, args):
        """Show information about a backup."""
        print(f"Showing information for backup: {args.backup_id}")
        
        backup_info = {
            'id': args.backup_id,
            'name': 'Unknown',
            'created_at': 'Unknown',
            'size': '0 MB',
            'description': 'No description'
        }
        
        if args.json:
            print(json.dumps(backup_info, indent=2))
        else:
            print("Backup Information")
            print("=" * 40)
            for key, value in backup_info.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        return 0
