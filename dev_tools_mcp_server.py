"""
MCP Tool Integration Servers
Includes: Code Execution, Web Search, Git Integration, Docker, and Development Tools
"""

import os
import json
import subprocess
import requests
import asyncio
import sys
from pathlib import Path
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# Initialize MCP Server
server = Server("tool-integration-mcp")

# ============ 1. CODE EXECUTION SERVER ============

class CodeExecutor:
    """Execute Python, JavaScript, and Bash code safely"""
    
    TIMEOUT = 30
    
    @staticmethod
    def execute_python(code: str) -> dict:
        try:
            result = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                timeout=CodeExecutor.TIMEOUT
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Code execution timed out"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def execute_javascript(code: str) -> dict:
        try:
            result = subprocess.run(
                ["node", "-e", code],
                capture_output=True,
                text=True,
                timeout=CodeExecutor.TIMEOUT
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Code execution timed out"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def execute_bash(command: str) -> dict:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=CodeExecutor.TIMEOUT
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command execution timed out"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def execute(language: str, code: str) -> dict:
        if language == "python":
            return CodeExecutor.execute_python(code)
        elif language == "javascript":
            return CodeExecutor.execute_javascript(code)
        elif language == "bash":
            return CodeExecutor.execute_bash(code)
        else:
            return {"error": f"Unsupported language: {language}"}


# ============ 2. WEB SEARCH SERVER ============

class SearchEngine:
    """Search the web and local documents"""
    
    @staticmethod
    def web_search(query: str, num_results: int = 5) -> dict:
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "max_results": num_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            
            if "Abstract" in data and data["Abstract"]:
                results.append({
                    "type": "abstract",
                    "title": data.get("Heading", ""),
                    "content": data["Abstract"],
                    "url": data.get("AbstractURL", "")
                })
            
            for topic in data.get("RelatedTopics", [])[:num_results]:
                if "Text" in topic:
                    results.append({
                        "type": "topic",
                        "title": topic.get("FirstURL", "").split("/")[-1],
                        "content": topic["Text"],
                        "url": topic.get("FirstURL", "")
                    })
            
            return {
                "success": True,
                "query": query,
                "results": results[:num_results],
                "count": len(results)
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def search_local_files(query: str, search_dir: str) -> dict:
        try:
            results = []
            search_path = Path(search_dir)
            
            if not search_path.exists():
                return {"error": f"Directory not found: {search_dir}"}
            
            for file_path in search_path.rglob("*.txt"):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            lines = content.split('\n')
                            matching_lines = [line for line in lines if query.lower() in line.lower()]
                            results.append({
                                "file": str(file_path),
                                "matches": len(matching_lines),
                                "preview": matching_lines[:3]
                            })
                except:
                    pass
            
            return {
                "success": True,
                "query": query,
                "search_dir": search_dir,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"error": str(e)}


# ============ 3. GIT INTEGRATION SERVER ============

class GitTools:
    """Git operations"""
    
    @staticmethod
    def get_status(repo_path: str) -> dict:
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
            return {
                "success": result.returncode == 0,
                "repo": repo_path,
                "changes": changes,
                "change_count": len(changes)
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_log(repo_path: str, num_commits: int = 5) -> dict:
        try:
            result = subprocess.run(
                ["git", "log", f"-{num_commits}", "--oneline"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
            return {
                "success": result.returncode == 0,
                "repo": repo_path,
                "commits": commits,
                "count": len(commits)
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def pull_changes(repo_path: str) -> dict:
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=15
            )
            return {
                "success": result.returncode == 0,
                "repo": repo_path,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def commit_changes(repo_path: str, message: str, files: list = None) -> dict:
        try:
            if files:
                subprocess.run(["git", "add"] + files, cwd=repo_path, capture_output=True, timeout=10)
            else:
                subprocess.run(["git", "add", "-A"], cwd=repo_path, capture_output=True, timeout=10)
            
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "success": result.returncode == 0,
                "repo": repo_path,
                "message": message,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def push_changes(repo_path: str) -> dict:
        try:
            result = subprocess.run(
                ["git", "push"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=15
            )
            return {
                "success": result.returncode == 0,
                "repo": repo_path,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"error": str(e)}


# ============ 4. DOCKER INTEGRATION SERVER ============

class DockerTools:
    """Docker operations"""
    
    @staticmethod
    def list_containers(running_only: bool = False) -> dict:
        try:
            cmd = ["docker", "ps"]
            if not running_only:
                cmd.append("-a")
            cmd.append("--format=json")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                containers = json.loads(result.stdout) if result.stdout else []
                return {"success": True, "containers": containers, "count": len(containers)}
            else:
                return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def start_container(container_id: str) -> dict:
        try:
            result = subprocess.run(
                ["docker", "start", container_id],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "success": result.returncode == 0,
                "container": container_id,
                "message": result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def stop_container(container_id: str) -> dict:
        try:
            result = subprocess.run(
                ["docker", "stop", container_id],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "success": result.returncode == 0,
                "container": container_id,
                "message": result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_logs(container_id: str, tail: int = 50) -> dict:
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(tail), container_id],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                "success": result.returncode == 0,
                "container": container_id,
                "logs": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"error": str(e)}


# ============ TOOL HANDLERS ============

@server.call_tool()
async def handle_tool_call(name: str, arguments: dict) -> Any:
    """Route tool calls"""
    
    try:
        if name == "execute_code":
            return CodeExecutor.execute(arguments.get("language"), arguments.get("code"))
        elif name == "web_search":
            return SearchEngine.web_search(arguments.get("query"), arguments.get("num_results", 5))
        elif name == "search_local":
            return SearchEngine.search_local_files(arguments.get("query"), arguments.get("directory"))
        elif name == "git_status":
            return GitTools.get_status(arguments.get("repo_path"))
        elif name == "git_log":
            return GitTools.get_log(arguments.get("repo_path"), arguments.get("num_commits", 5))
        elif name == "git_pull":
            return GitTools.pull_changes(arguments.get("repo_path"))
        elif name == "git_commit":
            return GitTools.commit_changes(arguments.get("repo_path"), arguments.get("message"), arguments.get("files"))
        elif name == "git_push":
            return GitTools.push_changes(arguments.get("repo_path"))
        elif name == "docker_list":
            return DockerTools.list_containers(arguments.get("running_only", False))
        elif name == "docker_start":
            return DockerTools.start_container(arguments.get("container_id"))
        elif name == "docker_stop":
            return DockerTools.stop_container(arguments.get("container_id"))
        elif name == "docker_logs":
            return DockerTools.get_logs(arguments.get("container_id"), arguments.get("tail", 50))
        else:
            return {"error": f"Unknown tool: {name}"}
    except Exception as e:
        return {"error": f"Tool execution error: {str(e)}"}


# ============ REGISTER TOOLS ============

tools = [
    types.Tool(
        name="execute_code",
        description="Execute code in Python, JavaScript, or Bash",
        inputSchema={
            "type": "object",
            "properties": {
                "language": {"type": "string", "enum": ["python", "javascript", "bash"], "description": "Programming language"},
                "code": {"type": "string", "description": "Code to execute"}
            },
            "required": ["language", "code"]
        }
    ),
    types.Tool(
        name="web_search",
        description="Search the web for information",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "description": "Number of results", "default": 5}
            },
            "required": ["query"]
        }
    ),
    types.Tool(
        name="search_local",
        description="Search local files for text content",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term"},
                "directory": {"type": "string", "description": "Directory to search"}
            },
            "required": ["query", "directory"]
        }
    ),
    types.Tool(name="git_status", description="Get git repository status",
        inputSchema={"type": "object", "properties": {"repo_path": {"type": "string"}}, "required": ["repo_path"]}),
    types.Tool(name="git_log", description="Get recent commits",
        inputSchema={"type": "object", "properties": {"repo_path": {"type": "string"}, "num_commits": {"type": "integer", "default": 5}}, "required": ["repo_path"]}),
    types.Tool(name="git_pull", description="Pull latest changes",
        inputSchema={"type": "object", "properties": {"repo_path": {"type": "string"}}, "required": ["repo_path"]}),
    types.Tool(name="git_commit", description="Commit changes",
        inputSchema={"type": "object", "properties": {"repo_path": {"type": "string"}, "message": {"type": "string"}, "files": {"type": "array"}}, "required": ["repo_path", "message"]}),
    types.Tool(name="git_push", description="Push changes to remote",
        inputSchema={"type": "object", "properties": {"repo_path": {"type": "string"}}, "required": ["repo_path"]}),
    types.Tool(name="docker_list", description="List Docker containers",
        inputSchema={"type": "object", "properties": {"running_only": {"type": "boolean", "default": False}}}),
    types.Tool(name="docker_start", description="Start a Docker container",
        inputSchema={"type": "object", "properties": {"container_id": {"type": "string"}}, "required": ["container_id"]}),
    types.Tool(name="docker_stop", description="Stop a Docker container",
        inputSchema={"type": "object", "properties": {"container_id": {"type": "string"}}, "required": ["container_id"]}),
    types.Tool(name="docker_logs", description="Get Docker container logs",
        inputSchema={"type": "object", "properties": {"container_id": {"type": "string"}, "tail": {"type": "integer", "default": 50}}, "required": ["container_id"]})
]

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return tools


# ============ START SERVER ============

# if __name__ == "__main__":
#     import logging
#     logging.basicConfig(level=logging.INFO)
    
#     print("Starting Tool Integration MCP Server...", file=sys.stderr, flush=True)
#     print(f"Tools available: {len(tools)}", file=sys.stderr, flush=True)
    
#     # Run with stdio transport
#     stdio_server(server).run()

# if __name__ == "__main__":
#     import logging
#     logging.basicConfig(level=logging.INFO)
    
#     print("Starting Tool Integration MCP Server...", file=sys.stderr, flush=True)
#     print(f"Tools available: {len(tools)}", file=sys.stderr, flush=True)
    
#     # Run with stdio transport
#     asyncio.run(stdio_server(server))


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Starting Tool Integration MCP Server...", file=sys.stderr, flush=True)
    print(f"Tools available: {len(tools)}", file=sys.stderr, flush=True)
    
    # Run with stdio transport
    async def main():
        async with stdio_server(server):
            print("Server is running...", file=sys.stderr, flush=True)
    
    asyncio.run(main())