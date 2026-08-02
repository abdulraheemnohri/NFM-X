"""
NFM-X CLI
"""
import asyncio
import click
from sdk.python.nfm import NFMClient, MemoryType, MemoryStatus, ChangeType

@click.group()
@click.option("--host", default="localhost")
@click.option("--port", default=8000, type=int)
@click.pass_context
def cli(ctx, host, port):
    ctx.obj = {"base_url": f"http://{host}:{port}"}

@cli.command()
@click.pass_context
def status(ctx):
    async def _status():
        async with NFMClient(base_url=ctx.obj["base_url"]) as client:
            health = await client.health_check()
            click.echo(f"Status: {health.get('status')}")
    asyncio.run(_status())

@cli.command()
@click.argument("query")
@click.option("--limit", default=10)
@click.pass_context
def search(ctx, query, limit):
    async def _search():
        async with NFMClient(base_url=ctx.obj["base_url"]) as client:
            results = await client.search(query, limit=limit)
            for i, (mem, score) in enumerate(zip(results.results, results.scores), 1):
                click.echo(f"{i}. {mem.id} Score: {score:.2f}")
    asyncio.run(_search())

@cli.command()
@click.argument("memory_id")
@click.pass_context
def get(ctx, memory_id):
    async def _get():
        async with NFMClient(base_url=ctx.obj["base_url"]) as client:
            memory = await client.get_memory(memory_id)
            click.echo(f"ID: {memory.id}")
            click.echo(f"Content: {memory.content}")
    asyncio.run(_get())

@cli.command()
@click.argument("content")
@click.option("--type", "mem_type", type=click.Choice([t.value for t in MemoryType]))
@click.pass_context
def create(ctx, content, mem_type):
    async def _create():
        async with NFMClient(base_url=ctx.obj["base_url"]) as client:
            memory = await client.create_memory(content=content, memory_type=MemoryType(mem_type) if mem_type else None)
            click.echo(f"Created: {memory.id}")
    asyncio.run(_create())

@cli.command()
@click.argument("memory_id")
@click.argument("content")
@click.option("--change-type", type=click.Choice([c.value for c in ChangeType]), required=True)
@click.option("--reason", required=True)
@click.pass_context
def update(ctx, memory_id, content, change_type, reason):
    async def _update():
        async with NFMClient(base_url=ctx.obj["base_url"]) as client:
            await client.update_memory(memory_id, content, ChangeType(change_type), reason)
            click.echo(f"Updated: {memory_id}")
    asyncio.run(_update())

@cli.command()
@click.argument("memory_id")
@click.option("--status", type=click.Choice([s.value for s in MemoryStatus]), required=True)
@click.pass_context
def set_status(ctx, memory_id, status):
    async def _set():
        async with NFMClient(base_url=ctx.obj["base_url"]) as client:
            await client.update_memory_status(memory_id, MemoryStatus(status))
            click.echo(f"Status set: {status}")
    asyncio.run(_set())

@cli.command()
@click.argument("memory_id")
@click.pass_context
def delete(ctx, memory_id):
    async def _delete():
        async with NFMClient(base_url=ctx.obj["base_url"]) as client:
            await client.delete_memory(memory_id)
            click.echo(f"Deleted: {memory_id}")
    asyncio.run(_delete())

@cli.command()
@click.option("--limit", default=50)
@click.pass_context
def list(ctx, limit):
    async def _list():
        async with NFMClient(base_url=ctx.obj["base_url"]) as client:
            response = await client.list_memories(limit=limit)
            for i, mem in enumerate(response.memories, 1):
                click.echo(f"{i}. {mem.id} [{mem.memory_type.value}]")
    asyncio.run(_list())

if __name__ == "__main__":
    cli()