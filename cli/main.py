#!/usr/bin/env python3
"""
NFM-X CLI Main
==============

Main command-line interface implementation for NFM-X.

Urdu: NFM-X ke liye main CLI implementation
"""

import argparse
import json
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sdk_dir = os.path.join(parent_dir, "sdk", "python")
if os.path.exists(sdk_dir) and sdk_dir not in sys.path:
    sys.path.insert(0, sdk_dir)

try:
    from nfm import NFMClient, MemoryCreate, SearchQuery, MemoryType
    from nfm.models import ContextQuery, EvolutionQuery, GraphQuery, AgentQuery
except ImportError:
    from nfm.client import NFMClient
    from nfm.models import (
        MemoryCreate, SearchQuery, ContextQuery, 
        EvolutionQuery, GraphQuery, AgentQuery, MemoryType
    )


class CLIFormatter:
    @staticmethod
    def format_memory(memory: Dict[str, Any]) -> str:
        memory_type = memory.get('memory_type', 'unknown')
        content = memory.get('content', '')
        memory_id = memory.get('id', 'unknown')
        confidence = memory.get('confidence', 0.0)
        timestamp = memory.get('created_at', '')
        if len(content) > 100:
            content = content[:97] + "..."
        return f"""Memory ID: {memory_id}
Type: {memory_type}
Confidence: {confidence:.2f}
Timestamp: {timestamp}
Content: {content}"""
    
    @staticmethod
    def format_search_result(result: Dict[str, Any]) -> str:
        memory_id = result.get('memory_id', 'unknown')
        content = result.get('content', '')
        score = result.get('similarity_score', 0.0)
        memory_type = result.get('memory_type', 'unknown')
        if len(content) > 80:
            content = content[:77] + "..."
        return f"[{memory_id}] {memory_type} ({score:.3f}): {content}"
    
    @staticmethod
    def format_list(memories: List[Dict[str, Any]], limit: int = 10) -> str:
        if not memories:
            return "No memories found."
        lines = []
        for i, memory in enumerate(memories[:limit]):
            memory_id = memory.get('id', 'unknown')
            memory_type = memory.get('memory_type', 'unknown')
            content = memory.get('content', '')[:50]
            confidence = memory.get('confidence', 0.0)
            lines.append(f"{i+1}. [{memory_id[:8]}...] {memory_type} ({confidence:.2f}): {content}")
        if len(memories) > limit:
            lines.append(f"... and {len(memories) - limit} more")
        return "\n".join(lines)
    
    @staticmethod
    def format_error(error: str) -> str:
        return f"Error: {error}"
    
    @staticmethod
    def format_success(message: str) -> str:
        return f"Success: {message}"


class NFMXCLI:
    def __init__(self):
        self.client = None
        self.formatter = CLIFormatter()
        self.base_url = "http://localhost:8000"
    
    def connect(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        try:
            url = base_url or self.base_url
            self.client = NFMClient(base_url=url, api_key=api_key)
            health = self.client.health_check()
            if health.success:
                print(self.formatter.format_success(f"Connected to NFM-X at {url}"))
                return True
            else:
                print(self.formatter.format_error(f"Failed to connect: {health.error}"))
                return False
        except Exception as e:
            print(self.formatter.format_error(str(e)))
            return False
    
    def memory_commands(self, args):
        if args.action == "create":
            self.create_memory(args)
        elif args.action == "get":
            self.get_memory(args)
        elif args.action == "list":
            self.list_memories(args)
        elif args.action == "delete":
            self.delete_memory(args)
        elif args.action == "update":
            self.update_memory(args)
    
    def create_memory(self, args):
        if not self.client:
            if not self.connect():
                return
        try:
            memory_type = None
            if args.type:
                try:
                    memory_type = MemoryType(args.type)
                except ValueError:
                    print(self.formatter.format_error(f"Invalid memory type: {args.type}"))
                    return
            
            metadata = {}
            if args.metadata:
                try:
                    metadata = json.loads(args.metadata)
                except json.JSONDecodeError:
                    print(self.formatter.format_error("Invalid metadata JSON"))
                    return
            
            tags = args.tags or []
            if isinstance(tags, str):
                tags = tags.split(",")
            
            memory = MemoryCreate(
                content=args.content, memory_type=memory_type,
                source=args.source, metadata=metadata, tags=tags,
                confidence=args.confidence
            )
            
            result = self.client.create_memory(memory)
            if result.success:
                memory_id = result.data.get('id', 'unknown')
                print(self.formatter.format_success(f"Memory created with ID: {memory_id}"))
            else:
                print(self.formatter.format_error(result.error or "Unknown error"))
                
        except Exception as e:
            print(self.formatter.format_error(str(e)))
    
    def get_memory(self, args):
        if not self.client:
            if not self.connect():
                return
        try:
            result = self.client.get_memory(args.memory_id)
            if result.success:
                print(self.formatter.format_memory(result.data))
            else:
                print(self.formatter.format_error(result.error or "Memory not found"))
                
        except Exception as e:
            print(self.formatter.format_error(str(e)))
    
    def list_memories(self, args):
        if not self.client:
            if not self.connect():
                return
        try:
            result = self.client.list_memories(
                memory_type=args.type, limit=args.limit or 100, offset=args.offset or 0
            )
            if result.success:
                memories = result.data if isinstance(result.data, list) else []
                print(f"Found {len(memories)} memories:")
                print(self.formatter.format_list(memories, args.limit or 100))
            else:
                print(self.formatter.format_error(result.error or "Failed to list memories"))
                
        except Exception as e:
            print(self.formatter.format_error(str(e)))
    
    def delete_memory(self, args):
        if not self.client:
            if not self.connect():
                return
        try:
            if not args.force:
                print(f"Are you sure you want to delete memory {args.memory_id}? (y/n)")
                response = input().strip().lower()
                if response != 'y' and response != 'yes':
                    print("Deletion cancelled.")
                    return
            result = self.client.delete_memory(args.memory_id)
            if result.success:
                print(self.formatter.format_success(f"Memory {args.memory_id} deleted"))
            else:
                print(self.formatter.format_error(result.error or "Failed to delete memory"))
                
        except Exception as e:
            print(self.formatter.format_error(str(e)))
    
    def update_memory(self, args):
        if not self.client:
            if not self.connect():
                return
        try:
            updates = {}
            if args.content:
                updates['content'] = args.content
            if args.type:
                try:
                    updates['memory_type'] = MemoryType(args.type)
                except ValueError:
                    print(self.formatter.format_error(f"Invalid memory type: {args.type}"))
                    return
            if args.metadata:
                try:
                    updates['metadata'] = json.loads(args.metadata)
                except json.JSONDecodeError:
                    print(self.formatter.format_error("Invalid metadata JSON"))
                    return
            if args.confidence is not None:
                updates['confidence'] = args.confidence
            if not updates:
                print(self.formatter.format_error("No updates provided"))
                return
            from nfm.models import MemoryUpdate
            memory_update = MemoryUpdate(**updates)
            result = self.client.update_memory(args.memory_id, memory_update)
            if result.success:
                print(self.formatter.format_success(f"Memory {args.memory_id} updated"))
            else:
                print(self.formatter.format_error(result.error or "Failed to update memory"))
                
        except Exception as e:
            print(self.formatter.format_error(str(e)))
    
    def search_memories(self, args):
        if not self.client:
            if not self.connect():
                return
        try:
            memory_types = None
            if args.type:
                try:
                    memory_types = [MemoryType(t) for t in args.type.split(",")]
                except ValueError as e:
                    print(self.formatter.format_error(f"Invalid memory type: {e}"))
                    return
            query = SearchQuery(
                query=args.query, memory_types=memory_types,
                strategy=args.strategy or "hybrid", limit=args.limit or 10,
                confidence_threshold=args.confidence
            )
            result = self.client.search_memories(query)
            if result.success:
                results = result.data if isinstance(result.data, list) else []
                if results:
                    print(f"Found {len(results)} results:")
                    for i, res in enumerate(results):
                        print(f"{i+1}. {self.formatter.format_search_result(res)}")
                else:
                    print("No results found.")
            else:
                print(self.formatter.format_error(result.error or "Search failed"))
                
        except Exception as e:
            print(self.formatter.format_error(str(e)))
    
    def get_context(self, args):
        if not self.client:
            if not self.connect():
                return
        try:
            query = ContextQuery(
                query=args.query, max_memories=args.limit or 20,
                time_window=args.time_window, include_relationships=not args.no_relationships
            )
            result = self.client.get_context(query)
            if result.success:
                context = result.data
                print(f"Context for: {args.query}")
                print(f"Confidence: {context.get('confidence', 0.0):.2f}")
                print(f"Memories found: {len(context.get('memories', []))}")
                summary = context.get('summary', '')
                print(f"Summary: {summary[:200]}{'...' if len(summary) > 200 else ''}")
            else:
                print(self.formatter.format_error(result.error or "Context query failed"))
                
        except Exception as e:
            print(self.formatter.format_error(str(e)))
    
    def info(self, args):
        if not self.client:
            if not self.connect():
                return
        try:
            result = self.client.get_info()
            if result.success:
                info = result.data
                print("NFM-X API Information:")
                print(f"Version: {info.get('version', 'unknown')}")
                print(f"Status: {info.get('status', 'unknown')}")
                print(f"Total Memories: {info.get('total_memories', 0)}")
                print(f"Memory Types: {', '.join(info.get('memory_types', []))}")
                print(f"Uptime: {info.get('uptime', 'unknown')}")
            else:
                print(self.formatter.format_error(result.error or "Failed to get info"))
                
        except Exception as e:
            print(self.formatter.format_error(str(e)))


def create_parser():
    parser = argparse.ArgumentParser(
        prog="nfm-x",
        description="NFM-X: Non-Forgettable Evolutionary AI Memory - Command Line Interface"
    )
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of NFM-X API")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    memory_parser = subparsers.add_parser("memory", help="Memory operations")
    memory_subparsers = memory_parser.add_subparsers(dest="action", help="Memory actions")
    
    create_parser = memory_subparsers.add_parser("create", help="Create a new memory")
    create_parser.add_argument("--content", "-c", required=True, help="Memory content")
    create_parser.add_argument("--type", "-t", help="Memory type")
    create_parser.add_argument("--source", "-s", help="Source of the memory")
    create_parser.add_argument("--metadata", "-m", help="Metadata as JSON")
    create_parser.add_argument("--tags", help="Comma-separated tags")
    create_parser.add_argument("--confidence", type=float, help="Confidence score (0-1)")
    
    get_parser = memory_subparsers.add_parser("get", help="Get a memory by ID")
    get_parser.add_argument("memory_id", help="Memory ID")
    
    list_parser = memory_subparsers.add_parser("list", help="List memories")
    list_parser.add_argument("--type", "-t", help="Filter by memory type")
    list_parser.add_argument("--limit", "-l", type=int, help="Maximum number of results")
    list_parser.add_argument("--offset", "-o", type=int, help="Pagination offset")
    
    delete_parser = memory_subparsers.add_parser("delete", help="Delete a memory")
    delete_parser.add_argument("memory_id", help="Memory ID")
    delete_parser.add_argument("--force", "-f", action="store_true", help="Force deletion without confirmation")
    
    update_parser = memory_subparsers.add_parser("update", help="Update a memory")
    update_parser.add_argument("memory_id", help="Memory ID")
    update_parser.add_argument("--content", "-c", help="New content")
    update_parser.add_argument("--type", "-t", help="New memory type")
    update_parser.add_argument("--metadata", "-m", help="New metadata as JSON")
    update_parser.add_argument("--confidence", type=float, help="New confidence score")
    
    search_parser = subparsers.add_parser("search", help="Search memories")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--type", "-t", help="Filter by memory types")
    search_parser.add_argument("--strategy", help="Search strategy")
    search_parser.add_argument("--limit", "-l", type=int, help="Maximum number of results")
    search_parser.add_argument("--confidence", type=float, help="Minimum confidence threshold")
    
    context_parser = subparsers.add_parser("context", help="Get context for a query")
    context_parser.add_argument("query", help="Context query")
    context_parser.add_argument("--limit", "-l", type=int, help="Maximum number of memories")
    context_parser.add_argument("--time-window", help="Time window")
    context_parser.add_argument("--no-relationships", action="store_true", help="Exclude relationships")
    
    subparsers.add_parser("info", help="Get API information")
    subparsers.add_parser("health", help="Check API health")
    
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    cli = NFMXCLI()
    cli.base_url = args.url
    if args.api_key:
        cli.connect(base_url=args.url, api_key=args.api_key)
    
    if args.command == "memory":
        cli.memory_commands(args)
    elif args.command == "search":
        cli.search_memories(args)
    elif args.command == "context":
        cli.get_context(args)
    elif args.command == "info":
        cli.info(args)
    elif args.command == "health":
        if cli.connect():
            result = cli.client.health_check()
            if result.success:
                print(cli.formatter.format_success("API is healthy"))
            else:
                print(cli.formatter.format_error(result.error or "API is not healthy"))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


# Urdu: NFM-X CLI main - Main CLI implementation ke liye