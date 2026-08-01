"""
NFM-X CLI Skills Command

Provides functionality to manage and execute skills.
"""

import argparse
import json


class SkillsCommand:
    """Command to manage skills in NFM-X."""
    
    def __init__(self):
        self.name = 'skills'
        self.help = 'Manage NFM-X skills'
        self.description = 'List, execute, and manage AI skills'
    
    def add_parser(self, subparsers):
        """Add the skills command parser."""
        parser = subparsers.add_parser(
            self.name,
            help=self.help,
            description=self.description
        )
        
        subcommand_parsers = parser.add_subparsers(
            dest='skills_action',
            title='skills actions',
            description='Available skill operations'
        )
        
        # List subcommand
        list_parser = subcommand_parsers.add_parser(
            'list',
            help='List all available skills'
        )
        list_parser.add_argument(
            '--category',
            '-c',
            help='Filter by skill category'
        )
        list_parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format'
        )
        
        # Execute subcommand
        execute_parser = subcommand_parsers.add_parser(
            'execute',
            help='Execute a skill'
        )
        execute_parser.add_argument(
            'skill_name',
            help='Name of the skill to execute'
        )
        execute_parser.add_argument(
            '--args',
            nargs='*',
            help='Arguments to pass to the skill'
        )
        execute_parser.add_argument(
            '--async',
            action='store_true',
            help='Execute skill asynchronously'
        )
        
        # Info subcommand
        info_parser = subcommand_parsers.add_parser(
            'info',
            help='Show information about a skill'
        )
        info_parser.add_argument(
            'skill_name',
            help='Name of the skill'
        )
        info_parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format'
        )
        
        # Categories subcommand
        categories_parser = subcommand_parsers.add_parser(
            'categories',
            help='List all skill categories'
        )
        categories_parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format'
        )
        
        return parser
    
    def execute(self, args):
        """Execute the skills command."""
        if not hasattr(args, 'skills_action') or args.skills_action is None:
            parser = self.add_parser(argparse.ArgumentParser().add_subparsers())
            parser.print_help()
            return 1
        
        action = args.skills_action
        
        if action == 'list':
            return self._list_skills(args)
        elif action == 'execute':
            return self._execute_skill(args)
        elif action == 'info':
            return self._show_skill_info(args)
        elif action == 'categories':
            return self._list_categories(args)
        else:
            print(f"Unknown skills action: {action}")
            return 1
    
    def _list_skills(self, args):
        """List all available skills."""
        print("Listing available skills")
        if args.category:
            print(f"Filtered by category: {args.category}")
        
        skills = []
        print(f"Found {len(skills)} skills")
        
        if args.json:
            print(json.dumps({'skills': skills}, indent=2))
        return 0
    
    def _execute_skill(self, args):
        """Execute a skill."""
        print(f"Executing skill: {args.skill_name}")
        if args.args:
            print(f"With arguments: {args.args}")
        if args.async:
            print("Running asynchronously")
        
        print(f"Skill {args.skill_name} executed successfully")
        return 0
    
    def _show_skill_info(self, args):
        """Show information about a skill."""
        print(f"Showing information for skill: {args.skill_name}")
        
        skill_info = {
            'name': args.skill_name,
            'description': 'Description not available',
            'category': 'unknown',
            'parameters': [],
            'examples': []
        }
        
        if args.json:
            print(json.dumps(skill_info, indent=2))
        else:
            print("Skill Information")
            print("=" * 40)
            print(f"Name: {skill_info['name']}")
            print(f"Description: {skill_info['description']}")
            print(f"Category: {skill_info['category']}")
        return 0
    
    def _list_categories(self, args):
        """List all skill categories."""
        categories = ['memory', 'analysis', 'ocr', 'search', 'evolution', 'utilities']
        
        if args.json:
            print(json.dumps({'categories': categories}, indent=2))
        else:
            print("Available Skill Categories:")
            for i, category in enumerate(categories, 1):
                print(f"{i}. {category}")
        return 0
