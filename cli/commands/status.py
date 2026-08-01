"""
NFM-X CLI Status Command

Provides system status information including memory count, storage usage, and service health.
"""

import argparse
import json
import sys
from datetime import datetime


class StatusCommand:
    """Command to check NFM-X system status."""
    
    def __init__(self):
        self.name = 'status'
        self.help = 'Check NFM-X system status and health'
        self.description = 'Display system status including memory statistics, storage usage, and service health'
    
    def add_parser(self, subparsers):
        """Add the status command parser."""
        parser = subparsers.add_parser(
            self.name,
            help=self.help,
            description=self.description
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output status in JSON format'
        )
        parser.add_argument(
            '--verbose',
            '-v',
            action='store_true',
            help='Show detailed status information'
        )
        return parser
    
    def execute(self, args):
        """Execute the status command."""
        status_data = self._get_status_data(args.verbose)
        
        if args.json:
            print(json.dumps(status_data, indent=2))
        else:
            self._print_status(status_data, args.verbose)
        
        return 0
    
    def _get_status_data(self, verbose=False):
        """Get status data for the system."""
        # This is a placeholder implementation
        # In a real implementation, this would connect to the NFM-X backend
        status_data = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'name': 'NFM-X',
                'version': '1.0.0',
                'status': 'running'
            },
            'memory': {
                'total_memories': 0,
                'active_memories': 0,
                'memory_types': {}
            },
            'storage': {
                'total_size': '0 MB',
                'used_size': '0 MB',
                'available_size': '0 MB'
            },
            'services': {
                'memory_service': 'healthy',
                'ocr_service': 'healthy',
                'knowledge_graph': 'healthy',
                'evolution_engine': 'healthy'
            }
        }
        
        if verbose:
            status_data['detailed'] = {
                'last_backup': None,
                'last_integrity_check': None,
                'system_uptime': '00:00:00',
                'active_connections': 0
            }
        
        return status_data
    
    def _print_status(self, status_data, verbose=False):
        """Print status information in a human-readable format."""
        print("NFM-X System Status")
        print("=" * 50)
        print(f"Timestamp: {status_data['timestamp']}")
        print(f"Version: {status_data['system']['version']}")
        print(f"Status: {status_data['system']['status']}")
        print()
        
        print("Memory Statistics:")
        print(f"  Total Memories: {status_data['memory']['total_memories']}")
        print(f"  Active Memories: {status_data['memory']['active_memories']}")
        print()
        
        print("Storage:")
        print(f"  Total: {status_data['storage']['total_size']}")
        print(f"  Used: {status_data['storage']['used_size']}")
        print(f"  Available: {status_data['storage']['available_size']}")
        print()
        
        print("Services:")
        for service, status in status_data['services'].items():
            print(f"  {service}: {status}")
        
        if verbose and 'detailed' in status_data:
            print()
            print("Detailed Information:")
            for key, value in status_data['detailed'].items():
                print(f"  {key.replace('_', ' ').title()}: {value}")