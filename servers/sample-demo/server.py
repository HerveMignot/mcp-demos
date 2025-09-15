from fastmcp import FastMCP

mcp = FastMCP("Sample Demo Server")

@mcp.tool()
def hello(name: str = "world") -> str:
    """A simple tool that returns a greeting."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()