import click
from rich.console import Console
from rich.table import Table
from rich.json import JSON
from sdk.python.nfm.client import NFMClient
from sdk.python.nfm.models import MemoryCreate, SearchQuery

console = Console()

def get_client():
    return NFMClient()

@click.group()
def cli():
    """NFM-X Command Line Interface"""
    pass

@cli.command()
def status():
    """Check server status"""
    client = get_client()
    try:
        health = client.health()
        console.print("[green]Server is healthy[/green]")
        console.print_json(data=health)
    except Exception as e:
        console.print(f"[red]Server unreachable: {e}[/red]")
    finally:
        client.close()

@cli.command()
@click.argument("query")
@click.option("--agent", "-a", help="Filter by agent ID")
@click.option("--limit", "-l", default=10, help="Max results")
def search(query, agent, limit):
    """Search memories"""
    client = get_client()
    try:
        result = client.search(SearchQuery(query=query, agent_id=agent, limit=limit))
        table = Table(title=f"Search: '{query}'")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Score", style="green")
        table.add_column("Content", style="white")

        for mem in result.get("results", []):
            table.add_row(
                mem.get("id", "")[:8] + "...",
                mem.get("type", ""),
                str(mem.get("score", 0)),
                mem.get("content", "")[:80]
            )
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        client.close()

@cli.command()
@click.argument("memory_id")
def get(memory_id):
    """Get memory details"""
    client = get_client()
    try:
        mem = client.get_memory(memory_id)
        console.print_json(data=mem)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        client.close()

@cli.command()
@click.argument("memory_id")
def history(memory_id):
    """Get memory history"""
    client = get_client()
    try:
        hist = client.get_history(memory_id)
        console.print_json(data=hist)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        client.close()

if __name__ == "__main__":
    cli()
