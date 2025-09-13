from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Sample Demo Server")

@mcp.tool()
def hello(name: str = "world") -> str:
    """A simple tool that returns a greeting."""
    return f"Hello, {name}!"

def run():
    mcp.run()

if __name__ == "__main__":
    run()
