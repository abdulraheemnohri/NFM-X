import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table

# Add root and SDK to path for correct importing
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "sdk" / "python"))

from nfm.client import NFMClient

app = typer.Typer(help="NFM-X Command Line Interface")
console = Console()


def get_client() -> NFMClient:
    """Helper to get pre-configured NFMClient"""
    base_url = os.environ.get("NFM_BASE_URL", "http://localhost:8000")
    api_key = os.environ.get("NFM_API_KEY")
    return NFMClient(base_url=base_url, api_key=api_key)


@app.command()
def create(
    content: str = typer.Argument(..., help="The content of the memory"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Title of the memory"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated list of tags"),
):
    """Create a new memory"""
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    async def _async_create():
        async with get_client() as client:
            memory = await client.create_memory(
                content=content,
                title=title,
                tags=tag_list,
                source="cli"
            )
            console.print(f"[green]Successfully created memory with ID: {memory.id}[/green]")
            console.print(f"Title: {memory.title}")
            console.print(f"Content: {memory.content}")

    asyncio.run(_async_create())


@app.command()
def get(
    memory_id: str = typer.Argument(..., help="The ID of the memory to fetch"),
):
    """Fetch a specific memory by its ID"""
    async def _async_get():
        async with get_client() as client:
            try:
                memory = await client.get_memory(memory_id)
                console.print(f"[green]Memory details for {memory_id}:[/green]")
                console.print(f"ID: {memory.id}")
                console.print(f"Title: {memory.title or 'Untitled'}")
                console.print(f"Content: {memory.content}")
                console.print(f"Tags: {', '.join(memory.tags)}")
                console.print(f"Created At: {memory.created_at}")
            except Exception as e:
                console.print(f"[red]Error fetching memory: {e}[/red]")

    asyncio.run(_async_get())


@app.command()
def search(
    query: str = typer.Argument(..., help="The search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Max number of results"),
):
    """Search memories using keyword and semantic retrieval"""
    async def _async_search():
        async with get_client() as client:
            try:
                response = await client.search(query=query, limit=limit)

                table = Table(title=f"Search Results for '{query}'")
                table.add_column("ID", style="cyan")
                table.add_column("Title", style="magenta")
                table.add_column("Content Preview", style="green")
                table.add_column("Relevance", style="yellow")

                for r in response.results:
                    table.add_row(r.id, r.title or "Untitled", r.content_preview[:50] + "...", f"{r.relevance_score:.2f}")

                console.print(table)
            except Exception as e:
                console.print(f"[red]Search failed: {e}[/red]")

    asyncio.run(_async_search())


@app.command()
def stats():
    """Get system memory statistics"""
    async def _async_stats():
        async with get_client() as client:
            try:
                response = await client.get_stats()
                console.print("[green]System Statistics:[/green]")
                console.print(f"Total Memories: {response.total_memories}")
                console.print(f"Active Memories: {response.active_memories}")
                console.print(f"Archived Memories: {response.archived_memories}")
            except Exception as e:
                console.print(f"[red]Failed to fetch stats: {e}[/red]")

    asyncio.run(_async_stats())


if __name__ == "__main__":
    app()
