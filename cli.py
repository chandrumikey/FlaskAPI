#!/usr/bin/env python3
import argparse
import uvicorn
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="FlashAPI CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run development server")
    run_parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    run_parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    run_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    run_parser.add_argument("--app", required=True, help="App import string (e.g., main:app)")
    
    # Create project command
    create_parser = subparsers.add_parser("create", help="Create new FlashAPI project")
    create_parser.add_argument("project_name", help="Name of the project")
    
    args = parser.parse_args()
    
    if args.command == "run":
        uvicorn.run(
            args.app,
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    elif args.command == "create":
        create_project(args.project_name)
    else:
        parser.print_help()

def create_project(project_name: str):
    """Create a new FlashAPI project structure"""
    project_dir = os.path.join(os.getcwd(), project_name)
    os.makedirs(project_dir, exist_ok=True)
    
    # Create main app file
    app_content = '''from flashapi import FlashAPI, get, post

app = FlashAPI(title="{}", version="1.0.0")

@app.get("/")
async def hello():
    return {{"message": "Welcome to {}!"}}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
'''.format(project_name, project_name)
    
    with open(os.path.join(project_dir, "main.py"), "w") as f:
        f.write(app_content)
    
    print(f"Created FlashAPI project: {project_name}")
    print(f"Directory: {project_dir}")
    print("Run with: python main.py")

if __name__ == "__main__":
    main()