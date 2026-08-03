#!/usr/bin/env python3
"""
NFM-X CLI
Command-line interface for the NFM-X memory system
"""
import asyncio
import click
import sys
import os
from typing import Optional, List

# Add the parent directory to Python path so we can import the SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'sdk', 'python'))

try:
    from nfm.client import NFMClient
    from nfm.config import get_config
except ImportError:
    # Fallback: try importing from installed package
    try:
        from sdk.python.nfm.client import NFMClient
        from sdk.python.nfm.config import get_config
    except ImportError:
        print("Error: NFM-X SDK not found. Please install it or run from the project root.")
        sys.exit(1)


@click.group()
@click.option('--host', default='localhost', help='NFM-X server host')
@click.option('--port', default=8000, type=int, help='NFM-X server port')
@click.option('--api-key', help='API key for authentication')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def cli(host: str, port: int, api_key: Optional[str], verbose: bool):
    """NFM-X Command Line Interface"""
    # Set up logging
    import logging
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Store context
    ctx = click.get_current_context()
    ctx.obj = {
        'host': host,
        'port': port,
        'api_key': api_key,
        'verbose': verbose
    }


@cli.command()
@click.option('--content', required=True, help='Content to store as memory')
@click.option('--title', help='Title for the memory')
@click.option('--tags', multiple=True, help='Tags for the memory')
@click.option('--memory-type', default='text', help='Type of memory')
def add(content: str, title: Optional[str], tags: List[str], memory_type: str):
    """Add a new memory"""
    ctx = click.get_current_context()
    obj = ctx.obj
    
    async def _add_memory():
        client = NFMClient(base_url=f"http://{obj['host']}:{obj['port']}")
        if obj['api_key']:
            client.set_api_key(obj['api_key'])
        
        try:
            memory = await client.create_memory(
                content=content,
                title=title,
                tags=list(tags),
                memory_type=memory_type
            )
            click.echo(f"Memory created with ID: {memory['id']}")
        except Exception as e:
            click.echo(f"Error creating memory: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_add_memory())


@cli.command()
@click.option('--limit', default=10, type=int, help='Number of memories to list')
@click.option('--search', help='Search query')
@click.option('--status', help='Filter by status')
def list(limit: int, search: Optional[str], status: Optional[str]):
    """List memories"""
    ctx = click.get_current_context()
    obj = ctx.obj
    
    async def _list_memories():
        client = NFMClient(base_url=f"http://{obj['host']}:{obj['port']}")
        if obj['api_key']:
            client.set_api_key(obj['api_key'])
        
        try:
            memories = await client.list_memories(limit=limit, search=search, status=status)
            if not memories:
                click.echo("No memories found")
                return
            
            for mem in memories:
                click.echo(f"ID: {mem['id']}")
                click.echo(f"  Title: {mem.get('title', 'No title')}")
                click.echo(f"  Content: {mem['content'][:100]}...")
                click.echo(f"  Status: {mem['status']}")
                click.echo(f"  Created: {mem['created_at']}")
                click.echo()
        except Exception as e:
            click.echo(f"Error listing memories: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_list_memories())


@cli.command()
@click.argument('memory_id')
def get(memory_id: str):
    """Get a specific memory"""
    ctx = click.get_current_context()
    obj = ctx.obj
    
    async def _get_memory():
        client = NFMClient(base_url=f"http://{obj['host']}:{obj['port']}")
        if obj['api_key']:
            client.set_api_key(obj['api_key'])
        
        try:
            memory = await client.get_memory(memory_id)
            click.echo(f"Memory {memory_id}:")
            click.echo(f"  Title: {memory.get('title', 'No title')}")
            click.echo(f"  Content: {memory['content']}")
            click.echo(f"  Status: {memory['status']}")
            click.echo(f"  Type: {memory.get('memory_type', 'text')}")
            click.echo(f"  Created: {memory['created_at']}")
            click.echo(f"  Access Count: {memory.get('access_count', 0)}")
        except Exception as e:
            click.echo(f"Error getting memory: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_get_memory())


@cli.command()
@click.argument('memory_id')
@click.option('--hard', is_flag=True, help='Permanently delete the memory')
def delete(memory_id: str, hard: bool):
    """Delete a memory"""
    ctx = click.get_current_context()
    obj = ctx.obj
    
    async def _delete_memory():
        client = NFMClient(base_url=f"http://{obj['host']}:{obj['port']}")
        if obj['api_key']:
            client.set_api_key(obj['api_key'])
        
        try:
            await client.delete_memory(memory_id, hard_delete=hard)
            click.echo(f"Memory {memory_id} deleted")
        except Exception as e:
            click.echo(f"Error deleting memory: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_delete_memory())


@cli.command()
@click.argument('query')
@click.option('--limit', default=5, type=int, help='Number of results to return')
def search(query: str, limit: int):
    """Search memories"""
    ctx = click.get_current_context()
    obj = ctx.obj
    
    async def _search_memories():
        client = NFMClient(base_url=f"http://{obj['host']}:{obj['port']}")
        if obj['api_key']:
            client.set_api_key(obj['api_key'])
        
        try:
            results = await client.search(query, limit=limit)
            if not results:
                click.echo("No results found")
                return
            
            for i, result in enumerate(results, 1):
                click.echo(f"Result {i} (Score: {result.get('score', 0):.3f}):")
                click.echo(f"  ID: {result['id']}")
                click.echo(f"  Content: {result['content'][:100]}...")
                click.echo()
        except Exception as e:
            click.echo(f"Error searching memories: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_search_memories())


@cli.command()
def stats():
    """Get system statistics"""
    ctx = click.get_current_context()
    obj = ctx.obj
    
    async def _get_stats():
        client = NFMClient(base_url=f"http://{obj['host']}:{obj['port']}")
        if obj['api_key']:
            client.set_api_key(obj['api_key'])
        
        try:
            stats = await client.get_stats()
            click.echo("NFM-X Statistics:")
            click.echo(f"  Total Memories: {stats.get('totalMemories', 0)}")
            click.echo(f"  Active Memories: {stats.get('activeMemories', 0)}")
            click.echo(f"  Total Versions: {stats.get('totalVersions', 0)}")
            click.echo(f"  Storage Size: {stats.get('totalStorageSize', 0)} bytes")
        except Exception as e:
            click.echo(f"Error getting statistics: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_get_stats())


@cli.command()
def health():
    """Check system health"""
    ctx = click.get_current_context()
    obj = ctx.obj
    
    async def _check_health():
        client = NFMClient(base_url=f"http://{obj['host']}:{obj['port']}")
        if obj['api_key']:
            client.set_api_key(obj['api_key'])
        
        try:
            healthy = await client.health_check()
            if healthy:
                click.echo("System is healthy ✓")
            else:
                click.echo("System is not healthy ✗", err=True)
                sys.exit(1)
        except Exception as e:
            click.echo(f"Error checking health: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_check_health())


if __name__ == '__main__':
    cli()