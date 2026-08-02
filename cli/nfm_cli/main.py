"""
NFM-X CLI
"""
import argparse
import asyncio
from app.main import app
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="NFM-X CLI")
    parser.add_argument("command", nargs="?")
    args = parser.parse_args()
    
    if args.command == "server":
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()