"""
MCP Database Query Tool Example
--------------------------------
Run this server:
    uv run mcp dev mcp_db_server.py

Then open MCP Inspector and connect using the local WebSocket URL shown in the terminal.
"""

from mcp.server.fastmcp import FastMCP
import sqlite3
from typing import Any

# Initialize MCP server
mcp = FastMCP("DBQueryServer")


# --- TOOL: Execute SQL queries on SQLite ---
@mcp.tool()
def query_database(db_path: str, query: str) -> list[dict[str, Any]]:
    """
    Execute a SQL query on a SQLite database.

    Args:
        db_path (str): Path to the SQLite database file.
        query (str): SQL query (SELECT, INSERT, UPDATE, DELETE, etc.)

    Returns:
        list[dict[str, Any]]: Query results (rows as dicts). 
                              Empty list if no rows returned.
    """
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Execute query
        cur.execute(query)

        # Commit if it's a write operation
        if query.strip().lower().startswith(("insert", "update", "delete", "create", "drop")):
            conn.commit()
            result = [{"status": "Query executed successfully"}]
        else:
            # For SELECT queries
            rows = cur.fetchall()
            result = [dict(row) for row in rows]

        cur.close()
        conn.close()
        return result

    except Exception as e:
        return [{"error": str(e)}]


# --- TOOL: Initialize a sample database ---
@mcp.tool()
def create_sample_db(db_path: str) -> str:
    """
    Create a sample 'users' table in SQLite database for demo/testing.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            city TEXT
        )
    """)
    cur.executemany(
        "INSERT INTO users (name, age, city) VALUES (?, ?, ?)",
        [("Alice", 25, "Imphal"), ("Bob", 30, "Delhi"), ("Charlie", 28, "Mumbai")]
    )
    conn.commit()
    conn.close()
    return f"Sample DB initialized at {db_path}"


# --- TOOL: Get all tables in a database ---
@mcp.tool()
def list_tables(db_path: str) -> list[str]:
    """
    List all table names in a SQLite database.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]
    conn.close()
    return tables


# Start MCP server
if __name__ == "__main__":
    mcp.run()
